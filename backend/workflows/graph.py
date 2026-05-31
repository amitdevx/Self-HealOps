from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from backend.workflows.state import IncidentState
from backend.agents.core import agent_system
import json
import asyncio
import logging

logger = logging.getLogger("workflow")

async def check_learning_node(state: IncidentState):
    from backend.services.learning import learning_service
    match = await learning_service.find_match(state["evidence"].strip())
    if match:
        from backend.agents.schemas import RemediationPlanResult, RootCauseResult, ActionModel
        import json
        rc_res = RootCauseResult(
            primary_root_cause=match.root_cause, 
            contributing_factors=[], 
            confidence=100.0, 
            recommended_remediation="Apply known deduplicated pattern"
        )
        plan_res = RemediationPlanResult(actions=[])
        try:
            parsed_actions = json.loads(match.resolution)
            plan_res = RemediationPlanResult(actions=[ActionModel(**a) for a in parsed_actions])
        except:
            pass
        return {"root_cause": rc_res, "remediation_plan": plan_res}
    return {}

async def classify_node(state: IncidentState):
    try:
        res = await asyncio.wait_for(agent_system.classify_failure(state["evidence"]), timeout=60.0)
        return {"classification": res}
    except asyncio.TimeoutError:
        logger.error(f"Timeout in classify_node for incident {state.get('incident_id')}")
        raise

async def rca_node(state: IncidentState):
    try:
        res = await asyncio.wait_for(agent_system.analyze_root_cause(state["evidence"]), timeout=60.0)
        return {"root_cause": res}
    except asyncio.TimeoutError:
        logger.error(f"Timeout in rca_node for incident {state.get('incident_id')}")
        raise

async def plan_node(state: IncidentState):
    rc = state["root_cause"].primary_root_cause if state["root_cause"] else ""
    try:
        res = await asyncio.wait_for(agent_system.plan_remediation(rc), timeout=60.0)
        return {"remediation_plan": res}
    except asyncio.TimeoutError:
        logger.error(f"Timeout in plan_node for incident {state.get('incident_id')}")
        raise

async def safety_node(state: IncidentState):
    plan_str = json.dumps([a.model_dump() for a in state["remediation_plan"].actions]) if state["remediation_plan"] else ""
    try:
        res = await asyncio.wait_for(agent_system.validate_safety(plan_str), timeout=60.0)
        return {"safety_validation": res}
    except asyncio.TimeoutError:
        logger.error(f"Timeout in safety_node for incident {state.get('incident_id')}")
        raise

async def execute_node(state: IncidentState):
    actions = state["remediation_plan"].actions if state["remediation_plan"] else []
    try:
        res = await asyncio.wait_for(agent_system.execute_plan(actions), timeout=60.0)
        return {"execution_result": res}
    except asyncio.TimeoutError:
        logger.error(f"Timeout in execute_node for incident {state.get('incident_id')}")
        raise

async def validate_node(state: IncidentState):
    try:
        res = await asyncio.wait_for(agent_system.validate_resolution(state["incident_id"]), timeout=60.0)
        return {"validation_result": res}
    except asyncio.TimeoutError:
        logger.error(f"Timeout in validate_node for incident {state.get('incident_id')}")
        raise

async def learn_node(state: IncidentState):
    try:
        res = await asyncio.wait_for(agent_system.extract_learning(state["evidence"]), timeout=60.0)
        return {"learning_result": res, "status": "RESOLVED"}
    except asyncio.TimeoutError:
        logger.error(f"Timeout in learn_node for incident {state.get('incident_id')}")
        raise

async def escalate_node(state: IncidentState):
    logger.critical(f"ESCALATION TRIGGERED for incident {state.get('incident_id', 'unknown')}")
    # Integration with PagerDuty or Slack would go here
    return {"status": "ESCALATED"}

async def retry_node(state: IncidentState):
    new_count = state.get("retry_count", 0) + 1
    logger.warning(f"Retrying remediation for incident {state.get('incident_id', 'unknown')}. Attempt {new_count}")
    return {"retry_count": new_count, "status": "RETRYING"}

def safety_edge(state: IncidentState):
    if state["safety_validation"] and state["safety_validation"].is_safe:
        return "execute"
    return "escalate"

def validation_edge(state: IncidentState):
    if state["validation_result"] and state["validation_result"].is_resolved:
        return "learn"
    if state["retry_count"] < 3:
        return "retry"
    return "escalate"

def check_learning_edge(state: IncidentState):
    if state.get("remediation_plan") and state["remediation_plan"].actions:
        return "safety"
    return "classify"

workflow = StateGraph(IncidentState)

workflow.add_node("check_learning", check_learning_node)
workflow.add_node("classify", classify_node)
workflow.add_node("rca", rca_node)
workflow.add_node("plan", plan_node)
workflow.add_node("safety", safety_node)
workflow.add_node("execute", execute_node)
workflow.add_node("validate", validate_node)
workflow.add_node("learn", learn_node)
workflow.add_node("escalate", escalate_node)
workflow.add_node("retry", retry_node)

workflow.set_entry_point("check_learning")
workflow.add_conditional_edges("check_learning", check_learning_edge, {"safety": "safety", "classify": "classify"})
workflow.add_edge("classify", "rca")
workflow.add_edge("rca", "plan")
workflow.add_edge("plan", "safety")

workflow.add_conditional_edges("safety", safety_edge, {"execute": "execute", "escalate": "escalate"})
workflow.add_edge("execute", "validate")
workflow.add_conditional_edges("validate", validation_edge, {"learn": "learn", "retry": "retry", "escalate": "escalate"})

workflow.add_edge("retry", "plan")
workflow.add_edge("learn", END)
workflow.add_edge("escalate", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
