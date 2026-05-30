from celery import Celery
from backend.core.config import settings
import asyncio
import logging
from backend.workflows.graph import app as workflow_app

logger = logging.getLogger(__name__)

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.task_routes = {
    "backend.workers.worker.process_incident": "main-queue"
}

@celery_app.task(name="backend.workers.worker.process_incident")
def process_incident(incident_id: str, evidence: str):
    logger.info(f"Starting async processing for incident: {incident_id}")
    
    # We must run the async LangGraph workflow inside a sync Celery task
    # using an event loop
    initial_state = {
        "incident_id": incident_id,
        "evidence": evidence,
        "classification": None,
        "root_cause": None,
        "remediation_plan": None,
        "safety_validation": None,
        "execution_result": None,
        "validation_result": None,
        "learning_result": None,
        "retry_count": 0,
        "status": "OPEN"
    }

    loop = asyncio.get_event_loop()
    final_state = loop.run_until_complete(
        workflow_app.ainvoke(
            initial_state, 
            config={"configurable": {"thread_id": incident_id}}
        )
    )
    
    logger.info(f"Finished processing incident: {incident_id}. Final status: {final_state.get('status')}")
    return final_state.get("status")
