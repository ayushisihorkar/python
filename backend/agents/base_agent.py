import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
import time
import json

from database.database import AsyncSessionLocal
from database.models import AgentAction

class BaseAgent(ABC):
    """Base class for all agents in the fleet maintenance system"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
        self.running = False
        self._task = None
        
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming data and return results"""
        pass
    
    async def start(self):
        """Start the agent"""
        self.running = True
        self.logger.info(f"{self.name} agent starting...")
        self._task = asyncio.create_task(self._run_loop())
        
    async def stop(self):
        """Stop the agent"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.logger.info(f"{self.name} agent stopped")
        
    async def _run_loop(self):
        """Main processing loop for the agent"""
        while self.running:
            try:
                await self._process_pending_actions()
                await asyncio.sleep(1)  # Prevent busy waiting
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in {self.name} agent loop: {e}")
                await asyncio.sleep(5)  # Back off on error
                
    async def _process_pending_actions(self):
        """Process any pending actions for this agent"""
        # Subclasses can override this for custom behavior
        pass
        
    async def log_action(
        self,
        action_type: str,
        vehicle_id: Optional[int] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        status: str = "completed",
        confidence_score: Optional[float] = None,
        processing_time: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> int:
        """Log an agent action to the database"""
        async with AsyncSessionLocal() as session:
            action = AgentAction(
                agent_name=self.name,
                action_type=action_type,
                vehicle_id=vehicle_id,
                input_data=input_data,
                output_data=output_data,
                status=status,
                confidence_score=confidence_score,
                processing_time=processing_time,
                error_message=error_message
            )
            session.add(action)
            await session.commit()
            await session.refresh(action)
            return action.id
            
    async def execute_with_logging(
        self,
        action_type: str,
        data: Dict[str, Any],
        vehicle_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute agent process with automatic logging"""
        start_time = time.time()
        action_id = None
        
        try:
            # Log start of action
            action_id = await self.log_action(
                action_type=action_type,
                vehicle_id=vehicle_id,
                input_data=data,
                status="processing"
            )
            
            # Process the data
            result = await self.process(data)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update action with results
            async with AsyncSessionLocal() as session:
                action = await session.get(AgentAction, action_id)
                if action:
                    action.output_data = result
                    action.status = "completed"
                    action.processing_time = processing_time
                    action.confidence_score = result.get("confidence", None)
                    await session.commit()
                    
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = str(e)
            
            # Update action with error
            if action_id:
                async with AsyncSessionLocal() as session:
                    action = await session.get(AgentAction, action_id)
                    if action:
                        action.status = "failed"
                        action.processing_time = processing_time
                        action.error_message = error_message
                        await session.commit()
                        
            self.logger.error(f"Error in {action_type}: {error_message}")
            raise
            
    def _calculate_confidence(self, metrics: Dict[str, float]) -> float:
        """Calculate confidence score based on various metrics"""
        # Simple confidence calculation - can be made more sophisticated
        total_score = 0
        count = 0
        
        for metric, value in metrics.items():
            if metric.endswith("_confidence"):
                total_score += value
                count += 1
                
        return total_score / count if count > 0 else 0.5