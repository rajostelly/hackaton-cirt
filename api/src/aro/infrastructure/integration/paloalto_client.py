from __future__ import annotations

import time
import xml.etree.ElementTree as ET  # noqa: N817
from xml.etree.ElementTree import Element

import httpx

from aro.domain.integration.value_objects import PaloAltoThreat


class PaloAltoClient:
    """Adaptateur Palo Alto NGFW — PAN-OS XML API (logs de type « threat »).

    La récupération de logs PAN-OS est asynchrone :
      1. on soumet une requête -> le firewall renvoie un job-id ;
      2. on interroge le job jusqu'au statut FIN -> il renvoie les entrées.

    Doc: https://docs.paloaltonetworks.com/pan-os/10-2/pan-os-panorama-api/get-started-with-the-pan-os-xml-api
    Auth: clé API passée en paramètre `key` (générée via type=keygen).
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        verify_ssl: bool = False,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._verify_ssl = verify_ssl
        self._timeout = timeout

    def get_recent_threats(self, limit: int = 50) -> list[PaloAltoThreat]:
        if not self._base_url or not self._api_key:
            raise RuntimeError("Palo Alto non configuré (PANOS_BASE_URL / PANOS_API_KEY)")
        with httpx.Client(verify=self._verify_ssl, timeout=self._timeout) as client:
            job_id = self._submit_query(client, limit)
            entries = self._poll_results(client, job_id)
        return [self._to_threat(e) for e in entries]

    def _submit_query(self, client: httpx.Client, limit: int) -> str:
        resp = client.get(
            f"{self._base_url}/api/",
            params={
                "type": "log",
                "log-type": "threat",
                "nlogs": str(limit),
                "key": self._api_key,
            },
        )
        resp.raise_for_status()
        root = ET.fromstring(resp.text)  # noqa: S314 - firewall de confiance
        job = root.findtext("./result/job")
        if job is None:
            raise RuntimeError(f"Requête de log PAN-OS échouée : {resp.text[:200]}")
        return job

    def _poll_results(
        self,
        client: httpx.Client,
        job_id: str,
        attempts: int = 10,
        delay: float = 1.0,
    ) -> list[Element]:
        for _ in range(attempts):
            resp = client.get(
                f"{self._base_url}/api/",
                params={
                    "type": "log",
                    "action": "get",
                    "job-id": job_id,
                    "key": self._api_key,
                },
            )
            resp.raise_for_status()
            root = ET.fromstring(resp.text)  # noqa: S314 - firewall de confiance
            if root.findtext("./result/job/status") == "FIN":
                return root.findall("./result/log/logs/entry")
            time.sleep(delay)
        return []

    @staticmethod
    def _to_threat(entry: Element) -> PaloAltoThreat:
        def field(tag: str) -> str:
            return entry.findtext(tag) or ""

        return PaloAltoThreat(
            id=field("seqno") or field("threatid") or entry.get("logid", ""),
            threat_name=field("threatid") or field("misc") or "threat",
            severity=field("severity") or "informational",
            action=field("action"),
            source_ip=field("src"),
            destination_ip=field("dst"),
            application=field("app") or None,
            timestamp=field("time_generated") or field("receive_time"),
        )
