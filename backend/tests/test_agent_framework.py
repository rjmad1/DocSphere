import unittest
import asyncio
from backend.services.agent_orchestrator.agent_framework import AgentOrchestrator, TaskRequest

class TestAgentFramework(unittest.TestCase):
    def setUp(self):
        self.orchestrator = AgentOrchestrator()

    def test_dispatch_task(self):
        task = TaskRequest(
            task_id="TASK-101",
            target_agent_id="AGT-ARCH",
            prompt_context={"doc_id": "DOC-BRD-001"},
            required_outputs=["adr_review"]
        )
        response = asyncio.run(self.orchestrator.dispatch_task(task))
        self.assertEqual(response.status, "COMPLETED")
        self.assertEqual(response.agent_id, "AGT-ARCH")

    def test_dispatch_invalid_agent(self):
        task = TaskRequest(
            task_id="TASK-102",
            target_agent_id="AGT-UNKNOWN",
            prompt_context={},
            required_outputs=[]
        )
        with self.assertRaises(ValueError):
            asyncio.run(self.orchestrator.dispatch_task(task))

if __name__ == "__main__":
    unittest.main()
