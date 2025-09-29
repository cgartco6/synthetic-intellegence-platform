from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio
import logging
import uuid
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type,
            'payload': self.payload,
            'status': self.status,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class BaseAgent(ABC):
    def __init__(self, name: str, capabilities: List[str], config: Dict[str, Any] = None):
        self.name = name
        self.capabilities = capabilities
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{name}")
        self._tasks: Dict[str, Task] = {}
        
    @abstractmethod
    async def execute(self, task: Task) -> Task:
        """Execute a task and return the result"""
        pass
    
    def can_handle(self, task_type: str) -> bool:
        """Check if this agent can handle a task type"""
        return task_type in self.capabilities
    
    async def validate_task(self, task: Task) -> bool:
        """Validate if the task can be processed"""
        if not self.can_handle(task.type):
            task.error = f"Agent {self.name} cannot handle task type: {task.type}"
            task.status = "failed"
            return False
        return True
    
    def create_task(self, task_type: str, payload: Dict[str, Any]) -> Task:
        """Create a new task"""
        task = Task(type=task_type, payload=payload)
        self._tasks[task.id] = task
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self._tasks.get(task_id)
    
    def get_tasks(self, status: str = None) -> List[Task]:
        """Get all tasks, optionally filtered by status"""
        if status:
            return [task for task in self._tasks.values() if task.status == status]
        return list(self._tasks.values())
    
    async def process_task(self, task: Task) -> Task:
        """Process a task with proper error handling"""
        try:
            if not await self.validate_task(task):
                return task
            
            task.status = "running"
            task.started_at = datetime.now()
            
            self.logger.info(f"Starting task {task.id} of type {task.type}")
            result = await self.execute(task)
            
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = result.result if isinstance(result, Task) else result
            
            self.logger.info(f"Completed task {task.id} successfully")
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()
            self.logger.error(f"Task {task.id} failed: {str(e)}")
        
        return task

class SyntheticIntelligenceMixin:
    """Mixin for synthetic intelligence capabilities"""
    
    async def learn_from_experience(self, experiences: List[Dict[str, Any]]):
        """Learn from past experiences"""
        self.logger.info(f"Learning from {len(experiences)} experiences")
        # Implement learning logic here
        pass
    
    async def adapt_behavior(self, feedback: Dict[str, Any]):
        """Adapt behavior based on feedback"""
        self.logger.info("Adapting behavior based on feedback")
        # Implement adaptation logic here
        pass
    
    async self_optimize(self):
        """Self-optimize the agent's performance"""
        self.logger.info("Running self-optimization")
        # Implement self-optimization logic here
        pass
