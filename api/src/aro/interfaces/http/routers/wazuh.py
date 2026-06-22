from fastapi import APIRouter, Depends

from aro.application.integration.use_cases import (
    GetWazuhAlertsUseCase,
    ListWazuhAgentsUseCase,
)
from aro.interfaces.http.dependencies import (
    get_list_wazuh_agents_use_case,
    get_wazuh_alerts_use_case,
)
from aro.interfaces.http.schemas.integration import WazuhAgentOut, WazuhAlertOut

router = APIRouter(prefix="/wazuh", tags=["wazuh"])


@router.get("/agents", response_model=list[WazuhAgentOut])
def list_agents(
    use_case: ListWazuhAgentsUseCase = Depends(get_list_wazuh_agents_use_case),
) -> list[WazuhAgentOut]:
    agents = use_case.execute()
    return [
        WazuhAgentOut(id=a.id, name=a.name, ip=a.ip, status=a.status, os_name=a.os_name)
        for a in agents
    ]


@router.get("/alerts", response_model=list[WazuhAlertOut])
def get_wazuh_alerts(
    limit: int = 50,
    use_case: GetWazuhAlertsUseCase = Depends(get_wazuh_alerts_use_case),
) -> list[WazuhAlertOut]:
    alerts = use_case.execute(limit=limit)
    return [
        WazuhAlertOut(
            id=a.id,
            rule_id=a.rule_id,
            rule_description=a.rule_description,
            rule_level=a.rule_level,
            agent_name=a.agent_name,
            source_ip=a.source_ip,
            timestamp=a.timestamp,
            full_log=a.full_log,
        )
        for a in alerts
    ]
