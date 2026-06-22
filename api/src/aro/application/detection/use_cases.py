from __future__ import annotations

from dataclasses import dataclass

from aro.application.alerting.dto import AlertOutput
from aro.application.alerting.use_cases import to_output
from aro.application.detection.dto import ScanDetectionInput
from aro.domain.alerting.entities import Alert
from aro.domain.alerting.ports import AlertRepository
from aro.domain.detection.services import classify_scan, scan_rule_name, scan_title
from aro.domain.shared.value_objects import IpAddress


@dataclass
class RecordScanDetectionUseCase:
    """Transforme un balayage réseau détecté en alerte de sécurité persistée."""

    repository: AlertRepository

    def execute(self, data: ScanDetectionInput) -> AlertOutput:
        port_count = len(data.ports)
        alert = Alert.create(
            title=scan_title(data.scan_type, data.source_ip, port_count),
            source_ip=IpAddress(data.source_ip),
            criticity=classify_scan(data.scan_type, port_count),
            rule_name=scan_rule_name(data.scan_type),
            raw_data={
                "scan_type": str(data.scan_type),
                "ports": data.ports,
                "target": data.target,
                "packet_count": data.packet_count,
                "detail": data.detail,
            },
        )
        self.repository.add(alert)
        return to_output(alert)
