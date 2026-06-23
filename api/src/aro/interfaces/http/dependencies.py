from __future__ import annotations

import os
from pathlib import Path

from fastapi import Depends

from aro.application.alerting.use_cases import (
    GetAlertUseCase,
    IngestAlertUseCase,
    ListOpenAlertsUseCase,
    TriageAlertUseCase,
)
from aro.application.detection.use_cases import RecordScanDetectionUseCase
from aro.application.incident.use_cases import (
    AnalyzeIncidentsUseCase,
    ListIncidentsUseCase,
    SimulateIncidentUseCase,
)
from aro.application.integration.use_cases import (
    EnrichAlertWithVirusTotalUseCase,
    GetCrowdStrikeDetectionsUseCase,
    GetPaloAltoThreatsUseCase,
    GetSocOverviewUseCase,
    GetWazuhAlertsUseCase,
    ListWazuhAgentsUseCase,
)
from aro.application.protection.use_cases import (
    AutoBlockUseCase,
    BlockIpUseCase,
    ListBlockedUseCase,
    UnblockIpUseCase,
)
from aro.application.virus.use_cases import ListVirusUseCase, LookupVirusUseCase
from aro.application.vulnerability.use_cases import (
    ListVulnerabilitiesUseCase,
    RefreshVulnerabilitiesUseCase,
)
from aro.domain.alerting.ports import AlertExplainer, AlertRepository
from aro.domain.incident.ports import IncidentRepository
from aro.domain.integration.ports import (
    CrowdStrikeGateway,
    PaloAltoGateway,
    VirusTotalGateway,
    WazuhIndexerGateway,
    WazuhManagerGateway,
)
from aro.domain.protection.ports import FirewallBlocker
from aro.domain.protection.value_objects import ProtectionMode
from aro.infrastructure.alerting.groq_explainer import GroqExplainer
from aro.infrastructure.alerting.memory_repo import InMemoryAlertRepository
from aro.infrastructure.alerting.static_explainer import StaticExplainer
from aro.infrastructure.incident.store import IncidentStore
from aro.infrastructure.integration.crowdstrike_client import CrowdStrikeClient
from aro.infrastructure.integration.paloalto_client import PaloAltoClient
from aro.infrastructure.integration.virustotal_client import VirusTotalClient
from aro.infrastructure.integration.wazuh_indexer_client import WazuhIndexerClient
from aro.infrastructure.integration.wazuh_manager_client import WazuhManagerClient
from aro.infrastructure.ml.report_repository import MlReportRepository
from aro.infrastructure.protection.memory_blocker import InMemoryBlocker
from aro.infrastructure.protection.settings import ProtectionSettings
from aro.infrastructure.realtime.broker import AlertBroker
from aro.infrastructure.virus.store import VirusStore
from aro.infrastructure.virus.vt_scanner import VtScanner
from aro.infrastructure.vulnerability.debsecan_collector import DebsecanCollector
from aro.infrastructure.vulnerability.report_repository import CveReportRepository

# ---------------------------------------------------------------------------
# Alerting singletons
# ---------------------------------------------------------------------------

_repository: AlertRepository | None = None
_broker = AlertBroker()


def get_repository() -> AlertRepository:
    """Repository d'alertes (singleton, choisi selon l'environnement).

    Avec `DATABASE_URL` (ex. Postgres), persistance SQLAlchemy ; sinon, dépôt
    en mémoire (tests, démo locale sans base).
    """
    global _repository
    if _repository is None:
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            from aro.infrastructure.alerting.session_repo import SessionScopedAlertRepository
            from aro.infrastructure.persistence.database import init_db

            _repository = SessionScopedAlertRepository(init_db(database_url))
        else:
            _repository = InMemoryAlertRepository()
    return _repository


def reset_repository() -> None:
    """Réinitialise le singleton (tests)."""
    global _repository
    _repository = None


def _maybe_session_factory():  # noqa: ANN202 - sessionmaker | None
    """Session factory SQLAlchemy si DATABASE_URL est défini, sinon None."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        return None
    from aro.infrastructure.persistence.database import init_db

    return init_db(url)


def get_broker() -> AlertBroker:
    return _broker


def get_explainer() -> AlertExplainer:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        # Pas de clé : explainer de repli, sans appel réseau (LSP-compatible).
        return StaticExplainer()
    return GroqExplainer(
        api_key=api_key,
        model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
    )


def get_record_scan_use_case(
    repo: AlertRepository = Depends(get_repository),
) -> RecordScanDetectionUseCase:
    return RecordScanDetectionUseCase(repository=repo)


def get_ingest_use_case(
    repo: AlertRepository = Depends(get_repository),
    explainer: AlertExplainer = Depends(get_explainer),
) -> IngestAlertUseCase:
    return IngestAlertUseCase(repository=repo, explainer=explainer)


def get_list_use_case(
    repo: AlertRepository = Depends(get_repository),
) -> ListOpenAlertsUseCase:
    return ListOpenAlertsUseCase(repository=repo)


def get_get_use_case(
    repo: AlertRepository = Depends(get_repository),
) -> GetAlertUseCase:
    return GetAlertUseCase(repository=repo)


def get_triage_use_case(
    repo: AlertRepository = Depends(get_repository),
) -> TriageAlertUseCase:
    return TriageAlertUseCase(repository=repo)


# ---------------------------------------------------------------------------
# Protection (IDS/IPS) singletons & use cases
# ---------------------------------------------------------------------------

_blocker: FirewallBlocker | None = None
_settings = ProtectionSettings(mode=ProtectionMode(os.environ.get("ARO_PROTECTION_MODE", "ids")))


def get_blocker() -> FirewallBlocker:
    """Bloqueur pare-feu : nftables si `ARO_FIREWALL=nft`, sinon en mémoire."""
    global _blocker
    if _blocker is None:
        if os.environ.get("ARO_FIREWALL") == "nft":
            from aro.infrastructure.protection.nft_blocker import NftBlocker

            _blocker = NftBlocker()
        else:
            _blocker = InMemoryBlocker()
    return _blocker


def reset_protection() -> None:
    """Réinitialise l'état protection (tests)."""
    global _blocker
    _blocker = None
    _settings.mode = ProtectionMode(os.environ.get("ARO_PROTECTION_MODE", "ids"))


def get_protection_settings() -> ProtectionSettings:
    return _settings


def get_protected_ips() -> frozenset[str]:
    return frozenset(o.strip() for o in os.environ.get("PROTECTED_IPS", "").split(",") if o.strip())


def get_block_use_case() -> BlockIpUseCase:
    return BlockIpUseCase(get_blocker(), get_protected_ips())


def get_unblock_use_case() -> UnblockIpUseCase:
    return UnblockIpUseCase(get_blocker())


def get_list_blocked_use_case() -> ListBlockedUseCase:
    return ListBlockedUseCase(get_blocker())


def auto_block(source_ip: str) -> bool:
    """Blocage auto en mode IPS (appelé par la chaîne de détection). Best-effort."""
    return AutoBlockUseCase(get_blocker(), get_protected_ips()).execute(
        source_ip, get_protection_settings().mode
    )


# ---------------------------------------------------------------------------
# Vulnerabilities (debsecan / CVE)
# ---------------------------------------------------------------------------

_cve_collector: DebsecanCollector | None = None


def get_cve_collector() -> DebsecanCollector:
    global _cve_collector
    if _cve_collector is None:
        _cve_collector = DebsecanCollector(suite=os.environ.get("DEBSECAN_SUITE", "trixie"))
    return _cve_collector


_cve_report_repo: CveReportRepository | None = None


def get_cve_report_repository() -> CveReportRepository:
    """Inventaire CVE : persisté en base si DATABASE_URL, sinon en mémoire."""
    global _cve_report_repo
    if _cve_report_repo is None:
        factory = _maybe_session_factory()
        if factory is not None:
            from aro.infrastructure.vulnerability.report_repository import SqlCveReportRepository

            _cve_report_repo = SqlCveReportRepository(factory)
        else:
            from aro.infrastructure.vulnerability.report_repository import (
                InMemoryCveReportRepository,
            )

            _cve_report_repo = InMemoryCveReportRepository()
    return _cve_report_repo


def reset_cve_report_repository() -> None:
    global _cve_report_repo
    _cve_report_repo = None


def get_list_vuln_use_case() -> ListVulnerabilitiesUseCase:
    return ListVulnerabilitiesUseCase(get_cve_report_repository())


def get_refresh_vuln_use_case() -> RefreshVulnerabilitiesUseCase:
    return RefreshVulnerabilitiesUseCase(get_cve_collector(), get_cve_report_repository())


# ---------------------------------------------------------------------------
# ML — détection d'anomalies (Isolation Forest). Imports paresseux (libs lourdes).
# ---------------------------------------------------------------------------

_ml_report_repo: MlReportRepository | None = None


def get_ml_plot_path() -> str:
    return os.environ.get("ML_PLOT_PATH", str(Path("static") / "ml" / "anomaly_dist.png"))


def get_ml_report_repository() -> MlReportRepository:
    """Rapports ML : persistés en base si DATABASE_URL, sinon en mémoire."""
    global _ml_report_repo
    if _ml_report_repo is None:
        factory = _maybe_session_factory()
        if factory is not None:
            from aro.infrastructure.ml.report_repository import SqlMlReportRepository

            _ml_report_repo = SqlMlReportRepository(factory)
        else:
            from aro.infrastructure.ml.report_repository import InMemoryMlReportRepository

            _ml_report_repo = InMemoryMlReportRepository()
    return _ml_report_repo


def reset_ml_report_repository() -> None:
    global _ml_report_repo
    _ml_report_repo = None


# ---------------------------------------------------------------------------
# Virus (VirusTotal)
# ---------------------------------------------------------------------------

_virus_store: VirusStore | None = None


def get_virus_store() -> VirusStore:
    global _virus_store
    if _virus_store is None:
        _virus_store = VirusStore()
    return _virus_store


def get_virus_scanner() -> VtScanner:
    return VtScanner(api_key=os.environ.get("VT_API_KEY", ""))


def get_list_virus_use_case() -> ListVirusUseCase:
    return ListVirusUseCase(get_virus_store())


def get_lookup_virus_use_case() -> LookupVirusUseCase:
    return LookupVirusUseCase(get_virus_scanner(), get_virus_store())


# ---------------------------------------------------------------------------
# Incidents (tshark : pic réseau, déplacement latéral)
# ---------------------------------------------------------------------------

_incident_repo: IncidentRepository | None = None


def get_incident_repository() -> IncidentRepository:
    """Incidents : persistés en base si DATABASE_URL, sinon en mémoire."""
    global _incident_repo
    if _incident_repo is None:
        factory = _maybe_session_factory()
        if factory is not None:
            from aro.infrastructure.incident.sql_repository import SqlIncidentRepository

            _incident_repo = SqlIncidentRepository(factory)
        else:
            _incident_repo = IncidentStore()
    return _incident_repo


def reset_incident_repository() -> None:
    global _incident_repo
    _incident_repo = None


def get_list_incidents_use_case() -> ListIncidentsUseCase:
    return ListIncidentsUseCase(get_incident_repository())


def get_simulate_incident_use_case() -> SimulateIncidentUseCase:
    return SimulateIncidentUseCase(get_incident_repository())


def get_analyze_incidents_use_case() -> AnalyzeIncidentsUseCase:
    from aro.infrastructure.incident.tshark_incident_collector import TsharkIncidentCollector

    collector = TsharkIncidentCollector(
        iface=os.environ.get("SENSOR_IFACE", "eth0"),
        duration=int(os.environ.get("INCIDENTS_CAPTURE_SECONDS", "8")),
    )
    return AnalyzeIncidentsUseCase(
        collector=collector,
        store=get_incident_repository(),
        spike_threshold=int(os.environ.get("INCIDENTS_SPIKE_THRESHOLD", "500")),
    )


def get_train_ml_use_case():  # noqa: ANN201 - type concret importé paresseusement
    from aro.application.ml.use_cases import TrainAnomalyModelUseCase
    from aro.infrastructure.ml.anomaly_pipeline import AnomalyPipeline
    from aro.infrastructure.ml.tshark_collector import TsharkCollector

    collector = TsharkCollector(
        iface=os.environ.get("SENSOR_IFACE", "eth0"),
        duration=int(os.environ.get("ML_CAPTURE_SECONDS", "10")),
    )
    return TrainAnomalyModelUseCase(
        collector=collector,
        pipeline=AnomalyPipeline(),
        repository=get_repository(),
        plot_path=get_ml_plot_path(),
    )


# ---------------------------------------------------------------------------
# Integration gateways — instanciés depuis les variables d'environnement
# ---------------------------------------------------------------------------

def get_vt_gateway() -> VirusTotalGateway:
    return VirusTotalClient(api_key=os.environ.get("VT_API_KEY", ""))


def get_wazuh_indexer_gateway() -> WazuhIndexerGateway:
    return WazuhIndexerClient(
        host=os.environ.get("WAZUH_INDEXER_HOST", "localhost"),
        port=int(os.environ.get("WAZUH_INDEXER_PORT", "9200")),
        user=os.environ.get("WAZUH_INDEXER_USER", "admin"),
        password=os.environ.get("WAZUH_INDEXER_PASSWORD", "admin"),
        verify_certs=os.environ.get("WAZUH_INDEXER_VERIFY_CERTS", "false").lower() == "true",
    )


def get_wazuh_manager_gateway() -> WazuhManagerGateway:
    return WazuhManagerClient(
        base_url=os.environ.get("WAZUH_MANAGER_URL", "https://localhost:55000"),
        user=os.environ.get("WAZUH_MANAGER_USER", "wazuh-wui"),
        password=os.environ.get("WAZUH_MANAGER_PASSWORD", "MyS3cr37P450r.*-"),
        verify_ssl=os.environ.get("WAZUH_MANAGER_VERIFY_SSL", "false").lower() == "true",
    )


def get_paloalto_gateway() -> PaloAltoGateway:
    return PaloAltoClient(
        base_url=os.environ.get("PANOS_BASE_URL", ""),
        api_key=os.environ.get("PANOS_API_KEY", ""),
        verify_ssl=os.environ.get("PANOS_VERIFY_SSL", "false").lower() == "true",
    )


def get_crowdstrike_gateway() -> CrowdStrikeGateway:
    return CrowdStrikeClient(
        base_url=os.environ.get("CROWDSTRIKE_BASE_URL", "https://api.crowdstrike.com"),
        client_id=os.environ.get("CROWDSTRIKE_CLIENT_ID", ""),
        client_secret=os.environ.get("CROWDSTRIKE_CLIENT_SECRET", ""),
        verify_ssl=os.environ.get("CROWDSTRIKE_VERIFY_SSL", "true").lower() == "true",
    )


# ---------------------------------------------------------------------------
# Integration use cases
# ---------------------------------------------------------------------------

def get_enrich_use_case(
    repo: AlertRepository = Depends(get_repository),
    vt: VirusTotalGateway = Depends(get_vt_gateway),
) -> EnrichAlertWithVirusTotalUseCase:
    return EnrichAlertWithVirusTotalUseCase(repository=repo, vt_gateway=vt)


def get_list_wazuh_agents_use_case(
    manager: WazuhManagerGateway = Depends(get_wazuh_manager_gateway),
) -> ListWazuhAgentsUseCase:
    return ListWazuhAgentsUseCase(wazuh_manager=manager)


def get_wazuh_alerts_use_case(
    indexer: WazuhIndexerGateway = Depends(get_wazuh_indexer_gateway),
) -> GetWazuhAlertsUseCase:
    return GetWazuhAlertsUseCase(wazuh_indexer=indexer)


def get_paloalto_threats_use_case(
    paloalto: PaloAltoGateway = Depends(get_paloalto_gateway),
) -> GetPaloAltoThreatsUseCase:
    return GetPaloAltoThreatsUseCase(paloalto=paloalto)


def get_crowdstrike_detections_use_case(
    crowdstrike: CrowdStrikeGateway = Depends(get_crowdstrike_gateway),
) -> GetCrowdStrikeDetectionsUseCase:
    return GetCrowdStrikeDetectionsUseCase(crowdstrike=crowdstrike)


def get_soc_overview_use_case(
    indexer: WazuhIndexerGateway = Depends(get_wazuh_indexer_gateway),
    paloalto: PaloAltoGateway = Depends(get_paloalto_gateway),
    crowdstrike: CrowdStrikeGateway = Depends(get_crowdstrike_gateway),
) -> GetSocOverviewUseCase:
    return GetSocOverviewUseCase(
        wazuh_indexer=indexer, paloalto=paloalto, crowdstrike=crowdstrike
    )
