import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .base_agent import BaseAgent, Task

class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue = asyncio.Queue()
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        self.logger = logging.getLogger("orchestrator")
        self._is_running = False
        self._workers = []
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
        
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(agent_name)
    
    def find_agent_for_task(self, task_type: str) -> Optional[BaseAgent]:
        """Find an agent capable of handling a task type"""
        for agent in self.agents.values():
            if agent.can_handle(task_type):
                return agent
        return None
    
    async def submit_task(self, task_type: str, payload: Dict[str, Any], 
                         agent_name: str = None) -> Optional[Task]:
        """Submit a task for processing"""
        agent = None
        
        if agent_name:
            agent = self.get_agent(agent_name)
            if not agent or not agent.can_handle(task_type):
                self.logger.error(f"Agent {agent_name} cannot handle task type {task_type}")
                return None
        else:
            agent = self.find_agent_for_task(task_type)
            if not agent:
                self.logger.error(f"No agent found for task type {task_type}")
                return None
        
        task = agent.create_task(task_type, payload)
        await self.task_queue.put((agent.name, task))
        self.logger.info(f"Submitted task {task.id} to {agent.name}")
        return task
    
    async def process_tasks(self, num_workers: int = 3):
        """Start processing tasks with multiple workers"""
        self._is_running = True
        self._workers = [asyncio.create_task(self._worker(i)) for i in range(num_workers)]
        self.logger.info(f"Started {num_workers} task workers")
        
    async def _worker(self, worker_id: int):
        """Worker process for handling tasks"""
        self.logger.info(f"Worker {worker_id} started")
        
        while self._is_running:
            try:
                # Wait for task with timeout
                agent_name, task = await asyncio.wait_for(
                    self.task_queue.get(), timeout=1.0
                )
                
                agent = self.get_agent(agent_name)
                if agent:
                    self.logger.info(f"Worker {worker_id} processing task {task.id}")
                    result_task = await agent.process_task(task)
                    
                    if result_task.status == "completed":
                        self.completed_tasks.append(result_task)
                    else:
                        self.failed_tasks.append(result_task)
                
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {str(e)}")
    
    async def stop(self):
        """Stop the orchestrator"""
        self._is_running = False
        await asyncio.gather(*self._workers, return_exceptions=True)
        self.logger.info("Orchestrator stopped")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and metrics"""
        total_tasks = len(self.completed_tasks) + len(self.failed_tasks)
        success_rate = (len(self.completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0
        
        agent_status = {}
        for agent_name, agent in self.agents.items():
            agent_tasks = agent.get_tasks()
            completed = len([t for t in agent_tasks if t.status == "completed"])
            failed = len([t for t in agent_tasks if t.status == "failed"])
            running = len([t for t in agent_tasks if t.status == "running"])
            
            agent_status[agent_name] = {
                'capabilities': agent.capabilities,
                'tasks_completed': completed,
                'tasks_failed': failed,
                'tasks_running': running,
                'success_rate': (completed / (completed + failed) * 100) if (completed + failed) > 0 else 0
            }
        
        return {
            'total_tasks_processed': total_tasks,
            'success_rate': success_rate,
            'queue_size': self.task_queue.qsize(),
            'agents': agent_status,
            'is_running': self._is_running
        }
    
    async def execute_workflow(self, workflow: List[Dict[str, Any]]) -> List[Task]:
        """Execute a workflow of tasks"""
        results = []
        
        for step in workflow:
            task_type = step['type']
            payload = step.get('payload', {})
            agent_name = step.get('agent')
            
            task = await self.submit_task(task_type, payload, agent_name)
            if task:
                # Wait for task completion
                while task.status in ['pending', 'running']:
                    await asyncio.sleep(0.1)
                    task = self.get_agent(agent_name).get_task(task.id) if agent_name else None
                
                results.append(task)
                
                # Check if we should continue on failure
                if task.status == 'failed' and not step.get('continue_on_failure', True):
                    break
        
        return results
