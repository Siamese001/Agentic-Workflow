"""
Delivery Worker
LEVEL 5 - Background worker for delivering outreach messages via various channels
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@dataclass
class DeliveryTask:
    """Represents a message delivery task"""
    task_id: str
    task_type: str
    outreach_content: Dict[str, str]
    delivery_config: Dict[str, Any]
    recipient_info: Dict[str, Any]
    sender_info: Dict[str, Any]
    priority: int = 1
    created_at: datetime = None
    status: str = "pending"

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class DeliveryResult:
    """Result of message delivery task"""
    task_id: str
    status: str
    delivery_channel: str
    delivery_timestamp: Optional[datetime] = None
    delivery_id: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    completed_at: datetime = None

    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.utcnow()

class DeliveryWorker:
    """Background worker for processing message delivery tasks"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Worker configuration
        self.worker_config = {
            "max_concurrent_tasks": 5,
            "task_timeout": 120,  # 2 minutes
            "retry_attempts": 3,
            "retry_delay": 5,  # seconds
            "queue_size": 100
        }

        # Delivery channel configurations
        self.delivery_channels = {
            "email": {
                "enabled": True,
                "rate_limit": 10,  # per minute
                "required_fields": ["to_email", "from_email", "subject", "body"],
                "retry_config": {"max_attempts": 3, "backoff": 2}
            },
            "linkedin": {
                "enabled": True,
                "rate_limit": 5,  # per minute
                "required_fields": ["recipient_profile_url", "message"],
                "retry_config": {"max_attempts": 2, "backoff": 1.5}
            },
            "sms": {
                "enabled": False,  # Requires SMS provider setup
                "rate_limit": 20,
                "required_fields": ["to_phone", "message"],
                "retry_config": {"max_attempts": 2, "backoff": 1}
            },
            "api_webhook": {
                "enabled": True,
                "rate_limit": 15,
                "required_fields": ["webhook_url", "payload"],
                "retry_config": {"max_attempts": 3, "backoff": 2}
            }
        }

        # Task management
        self.task_queue = asyncio.Queue(maxsize=self.worker_config["queue_size"])
        self.active_tasks = {}
        self.completed_tasks = {}
        self.task_results = {}

        # Worker state
        self.is_running = False
        self.worker_tasks = []
        self.stats = {
            "tasks_processed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_processing_time": 0.0,
            "worker_start_time": None,
            "deliveries_by_channel": {}
        }

        # Rate limiting
        self.rate_limiters = {
            channel: {"count": 0, "reset_time": datetime.utcnow()}
            for channel in self.delivery_channels.keys()
        }

    async def start(self):
        """Start the delivery worker"""
        try:
            self.logger.info("Starting delivery worker")

            if self.is_running:
                self.logger.warning("Worker is already running")
                return

            self.is_running = True
            self.stats["worker_start_time"] = datetime.utcnow()

            # Start worker tasks
            for i in range(self.worker_config["max_concurrent_tasks"]):
                worker_task = asyncio.create_task(self._worker_loop(f"delivery-worker-{i}"))
                self.worker_tasks.append(worker_task)

            # Start rate limit reset task
            rate_limit_task = asyncio.create_task(self._rate_limit_loop())
            self.worker_tasks.append(rate_limit_task)

            # Start cleanup task
            cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.worker_tasks.append(cleanup_task)

            self.logger.info(f"Started {self.worker_config['max_concurrent_tasks']} delivery worker tasks")

        except Exception as e:
            self.logger.error(f"Failed to start delivery worker: {e}")
            raise e

    async def stop(self):
        """Stop the delivery worker"""
        try:
            self.logger.info("Stopping delivery worker")

            if not self.is_running:
                self.logger.warning("Worker is not running")
                return

            self.is_running = False

            # Cancel all worker tasks
            for task in self.worker_tasks:
                task.cancel()

            # Wait for tasks to complete
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)

            self.logger.info("Delivery worker stopped successfully")

        except Exception as e:
            self.logger.error(f"Error stopping delivery worker: {e}")
            raise e

    async def submit_task(self, task_data: Dict[str, Any]) -> str:
        """Submit a new delivery task"""
        try:
            # Validate delivery channel
            channel = task_data["delivery_config"]["channel"]
            if channel not in self.delivery_channels:
                raise ValueError(f"Unsupported delivery channel: {channel}")

            # Create task
            task = DeliveryTask(
                task_id=str(uuid.uuid4()),
                task_type=task_data.get("task_type", "message_delivery"),
                outreach_content=task_data["outreach_content"],
                delivery_config=task_data["delivery_config"],
                recipient_info=task_data["recipient_info"],
                sender_info=task_data["sender_info"],
                priority=task_data.get("priority", 1)
            )

            # Add to queue
            await self.task_queue.put(task)
            self.active_tasks[task.task_id] = task

            self.logger.info(f"Submitted delivery task {task.task_id} via {channel}")
            return task.task_id

        except Exception as e:
            self.logger.error(f"Failed to submit delivery task: {e}")
            raise e

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific delivery task"""
        try:
            # Check active tasks
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                return {
                    "task_id": task.task_id,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "task_type": task.task_type,
                    "delivery_channel": task.delivery_config.get("channel")
                }

            # Check completed results
            if task_id in self.task_results:
                result = self.task_results[task_id]
                return {
                    "task_id": result.task_id,
                    "status": result.status,
                    "delivery_channel": result.delivery_channel,
                    "completed_at": result.completed_at.isoformat(),
                    "delivery_id": result.delivery_id,
                    "processing_time": result.processing_time,
                    "error_message": result.error_message
                }

            return None

        except Exception as e:
            self.logger.error(f"Failed to get delivery task status: {e}")
            return None

    async def get_task_result(self, task_id: str) -> Optional[DeliveryResult]:
        """Get result of a specific delivery task"""
        return self.task_results.get(task_id)

    async def get_worker_stats(self) -> Dict[str, Any]:
        """Get delivery worker statistics"""
        uptime = None
        if self.stats["worker_start_time"]:
            uptime = (datetime.utcnow() - self.stats["worker_start_time"]).total_seconds()

        return {
            "is_running": self.is_running,
            "active_tasks": len(self.active_tasks),
            "queue_size": self.task_queue.qsize(),
            "completed_tasks": len(self.task_results),
            "stats": self.stats.copy(),
            "uptime_seconds": uptime,
            "worker_config": self.worker_config,
            "available_channels": [
                channel for channel, config in self.delivery_channels.items()
                if config["enabled"]
            ],
            "rate_limits": {
                channel: {
                    "current_count": limiter["count"],
                    "limit": self.delivery_channels[channel]["rate_limit"],
                    "reset_in": max(0, (limiter["reset_time"] - datetime.utcnow()).total_seconds())
                }
                for channel, limiter in self.rate_limiters.items()
            }
        }

    async def _worker_loop(self, worker_name: str):
        """Main worker loop for processing delivery tasks"""
        self.logger.info(f"Starting delivery worker loop for {worker_name}")

        while self.is_running:
            try:
                # Get task from queue
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )

                # Process task
                await self._process_task(task, worker_name)

            except asyncio.TimeoutError:
                # No task available, continue
                continue
            except Exception as e:
                self.logger.error(f"Delivery worker {worker_name} error: {e}")
                await asyncio.sleep(1)

        self.logger.info(f"Delivery worker loop {worker_name} stopped")

    async def _process_task(self, task: DeliveryTask, worker_name: str):
        """Process a single delivery task"""
        start_time = datetime.utcnow()

        try:
            self.logger.info(f"{worker_name} processing delivery task {task.task_id}")

            # Update task status
            task.status = "processing"

            # Check rate limits
            channel = task.delivery_config["channel"]
            await self._check_rate_limit(channel)

            # Deliver message
            delivery_result = await self._deliver_message(task)

            # Create successful result
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = DeliveryResult(
                task_id=task.task_id,
                status="completed",
                delivery_channel=channel,
                delivery_timestamp=datetime.utcnow(),
                delivery_id=delivery_result.get("delivery_id"),
                response_data=delivery_result.get("response_data"),
                processing_time=processing_time
            )

            # Store result
            self.task_results[task.task_id] = result
            self.completed_tasks[task.task_id] = task

            # Update stats
            self.stats["tasks_completed"] += 1
            self.stats["tasks_processed"] += 1
            self._update_average_processing_time(processing_time)

            # Update channel stats
            if channel not in self.stats["deliveries_by_channel"]:
                self.stats["deliveries_by_channel"][channel] = 0
            self.stats["deliveries_by_channel"][channel] += 1

            # Remove from active tasks
            self.active_tasks.pop(task.task_id, None)

            self.logger.info(f"{worker_name} completed delivery task {task.task_id} via {channel} in {processing_time:.2f}s")

        except Exception as e:
            # Handle task failure
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            error_message = str(e)
            self.logger.error(f"{worker_name} failed delivery task {task.task_id}: {error_message}")

            # Create failure result
            result = DeliveryResult(
                task_id=task.task_id,
                status="failed",
                delivery_channel=task.delivery_config.get("channel"),
                error_message=error_message,
                processing_time=processing_time
            )

            # Store result
            self.task_results[task.task_id] = result

            # Update stats
            self.stats["tasks_failed"] += 1
            self.stats["tasks_processed"] += 1

            # Remove from active tasks
            self.active_tasks.pop(task.task_id, None)

    async def _check_rate_limit(self, channel: str):
        """Check and enforce rate limits for delivery channel"""

        limiter = self.rate_limiters[channel]
        channel_config = self.delivery_channels[channel]

        # Reset counter if time window has passed
        if datetime.utcnow() >= limiter["reset_time"]:
            limiter["count"] = 0
            limiter["reset_time"] = datetime.utcnow() + timedelta(minutes=1)

        # Check if limit exceeded
        if limiter["count"] >= channel_config["rate_limit"]:
            wait_time = (limiter["reset_time"] - datetime.utcnow()).total_seconds()
            if wait_time > 0:
                self.logger.info(f"Rate limit reached for {channel}, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)

        # Increment counter
        limiter["count"] += 1

    async def _deliver_message(self, task: DeliveryTask) -> Dict[str, Any]:
        """Deliver message via specified channel"""

        channel = task.delivery_config["channel"]

        if channel == "email":
            return await self._deliver_email(task)
        elif channel == "linkedin":
            return await self._deliver_linkedin(task)
        elif channel == "sms":
            return await self._deliver_sms(task)
        elif channel == "api_webhook":
            return await self._deliver_webhook(task)
        else:
            raise ValueError(f"Unsupported delivery channel: {channel}")

    async def _deliver_email(self, task: DeliveryTask) -> Dict[str, Any]:
        """Deliver message via email"""

        try:
            # Get email configuration
            config = task.delivery_config
            smtp_config = config.get("smtp", {})

            # Create message
            msg = MIMEMultipart()
            msg['From'] = task.sender_info.get("email")
            msg['To'] = task.recipient_info.get("email")
            msg['Subject'] = task.outreach_content.get("subject", "Professional Connection")

            # Add body
            body = task.outreach_content.get("body", "")
            msg.attach(MIMEText(body, 'plain'))

            # Simulate email sending (in production, use actual SMTP)
            await asyncio.sleep(1.0)  # Simulate network delay

            delivery_id = f"email_{uuid.uuid4().hex[:8]}"

            return {
                "delivery_id": delivery_id,
                "response_data": {
                    "message": "Email sent successfully",
                    "recipient": task.recipient_info.get("email"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            raise Exception(f"Email delivery failed: {str(e)}")

    async def _deliver_linkedin(self, task: DeliveryTask) -> Dict[str, Any]:
        """Deliver message via LinkedIn"""

        try:
            # Get LinkedIn configuration
            config = task.delivery_config

            # Simulate LinkedIn API call
            await asyncio.sleep(2.0)  # Simulate API delay

            delivery_id = f"linkedin_{uuid.uuid4().hex[:8]}"

            return {
                "delivery_id": delivery_id,
                "response_data": {
                    "message": "LinkedIn message sent successfully",
                    "recipient_profile": task.recipient_info.get("profile_url"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            raise Exception(f"LinkedIn delivery failed: {str(e)}")

    async def _deliver_sms(self, task: DeliveryTask) -> Dict[str, Any]:
        """Deliver message via SMS"""

        try:
            # Get SMS configuration
            config = task.delivery_config

            # Simulate SMS API call
            await asyncio.sleep(0.5)  # Simulate API delay

            delivery_id = f"sms_{uuid.uuid4().hex[:8]}"

            return {
                "delivery_id": delivery_id,
                "response_data": {
                    "message": "SMS sent successfully",
                    "recipient": task.recipient_info.get("phone"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            raise Exception(f"SMS delivery failed: {str(e)}")

    async def _deliver_webhook(self, task: DeliveryTask) -> Dict[str, Any]:
        """Deliver message via API webhook"""

        try:
            # Get webhook configuration
            config = task.delivery_config
            webhook_url = config.get("webhook_url")

            # Prepare payload
            payload = {
                "outreach_content": task.outreach_content,
                "recipient_info": task.recipient_info,
                "sender_info": task.sender_info,
                "delivery_metadata": {
                    "task_id": task.task_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

            # Simulate webhook call
            await asyncio.sleep(1.5)  # Simulate network delay

            delivery_id = f"webhook_{uuid.uuid4().hex[:8]}"

            return {
                "delivery_id": delivery_id,
                "response_data": {
                    "message": "Webhook delivered successfully",
                    "webhook_url": webhook_url,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            raise Exception(f"Webhook delivery failed: {str(e)}")

    async def _rate_limit_loop(self):
        """Reset rate limit counters periodically"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Reset every minute

                for channel, limiter in self.rate_limiters.items():
                    limiter["count"] = 0
                    limiter["reset_time"] = datetime.utcnow() + timedelta(minutes=1)

                self.logger.debug("Rate limit counters reset")

            except Exception as e:
                self.logger.error(f"Rate limit loop error: {e}")

    async def _cleanup_loop(self):
        """Cleanup loop for removing old task results"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                # Remove results older than 6 hours
                cutoff_time = datetime.utcnow() - timedelta(hours=6)

                old_task_ids = [
                    task_id for task_id, result in self.task_results.items()
                    if result.completed_at < cutoff_time
                ]

                for task_id in old_task_ids:
                    self.task_results.pop(task_id, None)
                    self.completed_tasks.pop(task_id, None)

                if old_task_ids:
                    self.logger.info(f"Cleaned up {len(old_task_ids)} old delivery task results")

            except Exception as e:
                self.logger.error(f"Delivery cleanup loop error: {e}")

    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time statistic"""
        if self.stats["tasks_processed"] == 1:
            self.stats["average_processing_time"] = processing_time
        else:
            current_avg = self.stats["average_processing_time"]
            n = self.stats["tasks_processed"]
            self.stats["average_processing_time"] = ((current_avg * (n - 1)) + processing_time) / n

    async def get_delivery_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent delivery history"""

        # Sort completed tasks by completion time
        sorted_results = sorted(
            self.task_results.items(),
            key=lambda x: x[1].completed_at,
            reverse=True
        )

        history = []
        for task_id, result in sorted_results[:limit]:
            history.append({
                "task_id": result.task_id,
                "status": result.status,
                "delivery_channel": result.delivery_channel,
                "completed_at": result.completed_at.isoformat(),
                "delivery_id": result.delivery_id,
                "processing_time": result.processing_time
            })

        return history

# Global delivery worker instance
delivery_worker = DeliveryWorker()

__all__ = [
    "DeliveryWorker",
    "DeliveryTask",
    "DeliveryResult",
    "delivery_worker"
]
