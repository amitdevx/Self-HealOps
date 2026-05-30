from langgraph.graph import StateGraph, END
from backend.workflows.state import IncidentState
from backend.agents.core import agent_system
import json

async def classify_node(state: IncidentState):
    res = await agent_system.classify_failure(state["evidence"])
    return {"classification": res}

async def rca_node(state: IncidentState):
    res = await agent_system.analyze_root_cause(state["evidence"])
    return {"root_cause": res}

async def plan_node(state: IncidentState):
    rc = state["root_cause"].primary_root_cause if state["root_cause"] else ""
    res = await agent_system.plan_remediation(rc)
    return {"remediation_plan": res}

async def safety_node(state: IncidentState):
    plan_str = json.dumps([a for a in state["remediation_plan"].actions]) if state["remediation_plan"] else ""
    res = await agent_system.validate_safety(plan_str)
    return {"safety_validation": res}

async def execute_node(state: IncidentState):
    actions = state["remediation_plan"].actions if state["remediation_plan"] else []
    res = await agent_system.execute_plan(actions)
    return {"execution_result": res}

async def validate_node(state: IncidentState):
    res = await agent_system.validate_resolution(state["incident_id"])
    return {"validation_result": res}

async def learn_node(state: IncidentState):
    res = await agent_system.extract_learning(state["evidence"])
    return {"learning_result": res, "status": "RESOLVED"}

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

workflow = StateGraph(IncidentState)

workflow.add_node("classify", classify_node)
workflow.add_node("rca", rca_node)
workflow.add_node("plan", plan_node)
workflow.add_node("safety", safety_node)
workflow.add_node("execute", execute_node)
workflow.add_node("validate", validate_node)
workflow.add_node("learn", learn_node)
# escalations and retries can be external or dummy nodes
workflow.add_node("escalate", lambda s: {"status": "ESCALATED"})
workflow.add_node("retry", lambda s: {"retry_count": s["retry_count"] + 1, "status": "RETRYING"})

workflow.set_entry_point("classify")
workflow.add_edge("classify", "rca")
workflow.add_edge("rca", "plan")
workflow.add_edge("plan", "safety")

workflow.add_conditional_edges("safety", safety_edge, {"execute": "execute", "escalate": "escalate"})
workflow.add_edge("execute", "validate")
workflow.add_conditional_edges("validate", validation_edge, {"learn": "learn", "retry": "retry", "escalate": "escalate"})

workflow.add_edge("retry", "plan")
workflow.add_edge("learn", END)
workflow.add_edge("escalate", END)

app = workflow.compile()
