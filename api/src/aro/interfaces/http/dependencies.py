from __future__ import annotations

import os

from fastapi import Depends

from aro.application.alerting.use_cases import (
    GetAlertUseCase,
    IngestAlertUseCase,
    ListOpenAlertsUseCase,
    TriageAlertUseCase,
)
from aro.application.detection.use_cases import RecordScanDetectionUseCase
from aro.application.integration.use_cases import (
    EnrichAlertWithVirusTotalUseCase,
    GetCrowdStrikeDetectionsUseCase,
    GetPaloAltoThreatsUseCase,
    GetSocOverviewUseCase,
    GetWazuhAlertsUseCase,
    ListWazuhAgentsUseCase,
)
from aro.domain.alerting.ports import AlertExplainer, AlertRepository
from aro.domain.integration.ports import (
    CrowdStrikeGateway,
    PaloAltoGateway,
    VirusTotalGateway,
    WazuhIndexerGateway,
    WazuhManagerGateway,
)
from aro.infrastructure.alerting.groq_explainer import GroqExplainer
from aro.infrastructure.alerting.memory_repo import InMemoryAlertRepository
from aro.infrastructure.alerting.static_explainer import StaticExplainer
from aro.infrastructure.realtime.broker import AlertBroker
from aro.infrastructure.integration.crowdstrike_client import CrowdStrikeClient
from aro.infrastructure.integration.paloalto_client import PaloAltoClient
from aro.infrastructure.integration.virustotal_client import VirusTotalClient
from aro.infrastructure.integration.wazuh_indexer_client import WazuhIndexerClient
from aro.infrastructure.integration.wazuh_manager_client import WazuhManagerClient

# ---------------------------------------------------------------------------
# Alerting singletons
# ---------------------------------------------------------------------------

_repository: AlertRepository = InMemoryAlertRepository()
_broker = AlertBroker()


def get_repository() -> AlertRepository:
    return _repository


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
