import asyncio
import uuid
import sys
import logging
from backend.workflows.graph import app as workflow_app

logging.basicConfig(level=logging.INFO)

async def test_agent_real_life():
    incident_id = str(uuid.uuid4())
    
    evidence = """
GitHub Actions Workflow Failed: build-and-test
Repository: amitdevx/OG_GROUP
Commit: a1b2c3d
Branch: main

Logs:
Run pip install -r requirements.txt
...
Run pytest tests/
============================= test session starts ==============================
platform linux -- Python 3.12.2, pytest-8.1.1, pluggy-1.4.0
rootdir: /home/runner/work/Self-HealOps/Self-HealOps
collected 0 items / 1 error

==================================== ERRORS ====================================
_______________________ ERROR collecting tests/test_main.py _______________________
ImportError while importing test module '/home/runner/work/Self-HealOps/Self-HealOps/tests/test_main.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/hostedtoolcache/Python/3.12.2/x64/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_main.py:1: in <module>
    from backend.main import app
backend/main.py:2: in <module>
    from fastapi import FastAPI
E   ModuleNotFoundError: No module named 'fastapi'
=========================== short test summary info ============================
ERROR tests/test_main.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.12s ===============================
Error: Process completed with exit code 2.
    """
    
    print(f"Starting real life test for agent with incident: {incident_id}")
    
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

    final_state = await workflow_app.ainvoke(
        initial_state, 
        config={"configurable": {"thread_id": incident_id}}
    )
    
    print("\n--- Final State ---")
    print(f"Classification: {final_state.get('classification')}")
    print(f"Root Cause: {final_state.get('root_cause')}")
    print(f"Remediation Plan: {final_state.get('remediation_plan')}")
    print(f"Safety Validation: {final_state.get('safety_validation')}")
    print(f"Execution Result: {final_state.get('execution_result')}")
    print(f"Status: {final_state.get('status')}")

if __name__ == "__main__":
    asyncio.run(test_agent_real_life())
