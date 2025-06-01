"""
任务调度器模块
使用 APScheduler 进行任务调度
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config.settings import get_settings
from app.core.exceptions import SchedulerError
from app.core.logger import get_logger


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.logger = get_logger("scheduler")
        self._jobs: Dict[str, dict] = {}
        
    async def start(self) -> None:
        """启动调度器"""
        if self.scheduler is not None:
            self.logger.warning("Scheduler is already running")
            return
        
        try:
            self.scheduler = AsyncIOScheduler(
                timezone=self.settings.scheduler.timezone,
                job_defaults=self.settings.scheduler.job_defaults
            )
            
            self.scheduler.start()
            self.logger.info("Task scheduler started", timezone=self.settings.scheduler.timezone)
            
            # 添加默认的定时任务
            await self._add_default_jobs()
            
        except Exception as e:
            self.logger.error("Failed to start scheduler", error=str(e))
            raise SchedulerError(f"无法启动任务调度器: {e}")
    
    async def stop(self) -> None:
        """停止调度器"""
        if self.scheduler is None:
            self.logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.scheduler = None
            self.logger.info("Task scheduler stopped")
        except Exception as e:
            self.logger.error("Failed to stop scheduler", error=str(e))
            raise SchedulerError(f"无法停止任务调度器: {e}")
    
    async def add_cron_job(
        self,
        job_id: str,
        func,
        cron_expression: str,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
        replace_existing: bool = False
    ) -> None:
        """添加 cron 定时任务"""
        if self.scheduler is None:
            raise SchedulerError("调度器未启动")
        
        try:
            # 解析 cron 表达式
            parts = cron_expression.split()
            if len(parts) != 5:
                raise ValueError("Cron expression must have 5 parts")
            
            minute, hour, day, month, day_of_week = parts
            
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                timezone=self.settings.scheduler.timezone
            )
            
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                args=args,
                kwargs=kwargs,
                replace_existing=replace_existing
            )
            
            self._jobs[job_id] = {
                "type": "cron",
                "expression": cron_expression,
                "func": func.__name__ if hasattr(func, '__name__') else str(func),
                "created_at": datetime.now()
            }
            
            self.logger.info(
                "Cron job added",
                job_id=job_id,
                cron_expression=cron_expression,
                func=func.__name__ if hasattr(func, '__name__') else str(func)
            )
            
        except Exception as e:
            self.logger.error("Failed to add cron job", job_id=job_id, error=str(e))
            raise SchedulerError(f"无法添加定时任务 {job_id}: {e}")
    
    async def add_interval_job(
        self,
        job_id: str,
        func,
        seconds: int,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
        replace_existing: bool = False
    ) -> None:
        """添加间隔任务"""
        if self.scheduler is None:
            raise SchedulerError("调度器未启动")
        
        try:
            trigger = IntervalTrigger(seconds=seconds)
            
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                args=args,
                kwargs=kwargs,
                replace_existing=replace_existing
            )
            
            self._jobs[job_id] = {
                "type": "interval",
                "seconds": seconds,
                "func": func.__name__ if hasattr(func, '__name__') else str(func),
                "created_at": datetime.now()
            }
            
            self.logger.info(
                "Interval job added",
                job_id=job_id,
                interval_seconds=seconds,
                func=func.__name__ if hasattr(func, '__name__') else str(func)
            )
            
        except Exception as e:
            self.logger.error("Failed to add interval job", job_id=job_id, error=str(e))
            raise SchedulerError(f"无法添加间隔任务 {job_id}: {e}")
    
    async def add_date_job(
        self,
        job_id: str,
        func,
        run_date: datetime,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
        replace_existing: bool = False
    ) -> None:
        """添加定时任务（指定时间执行一次）"""
        if self.scheduler is None:
            raise SchedulerError("调度器未启动")
        
        try:
            trigger = DateTrigger(run_date=run_date)
            
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                args=args,
                kwargs=kwargs,
                replace_existing=replace_existing
            )
            
            self._jobs[job_id] = {
                "type": "date",
                "run_date": run_date,
                "func": func.__name__ if hasattr(func, '__name__') else str(func),
                "created_at": datetime.now()
            }
            
            self.logger.info(
                "Date job added",
                job_id=job_id,
                run_date=run_date.isoformat(),
                func=func.__name__ if hasattr(func, '__name__') else str(func)
            )
            
        except Exception as e:
            self.logger.error("Failed to add date job", job_id=job_id, error=str(e))
            raise SchedulerError(f"无法添加定时任务 {job_id}: {e}")
    
    async def remove_job(self, job_id: str) -> None:
        """移除任务"""
        if self.scheduler is None:
            raise SchedulerError("调度器未启动")
        
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self._jobs:
                del self._jobs[job_id]
            
            self.logger.info("Job removed", job_id=job_id)
            
        except Exception as e:
            self.logger.error("Failed to remove job", job_id=job_id, error=str(e))
            raise SchedulerError(f"无法移除任务 {job_id}: {e}")
    
    async def pause_job(self, job_id: str) -> None:
        """暂停任务"""
        if self.scheduler is None:
            raise SchedulerError("调度器未启动")
        
        try:
            self.scheduler.pause_job(job_id)
            self.logger.info("Job paused", job_id=job_id)
            
        except Exception as e:
            self.logger.error("Failed to pause job", job_id=job_id, error=str(e))
            raise SchedulerError(f"无法暂停任务 {job_id}: {e}")
    
    async def resume_job(self, job_id: str) -> None:
        """恢复任务"""
        if self.scheduler is None:
            raise SchedulerError("调度器未启动")
        
        try:
            self.scheduler.resume_job(job_id)
            self.logger.info("Job resumed", job_id=job_id)
            
        except Exception as e:
            self.logger.error("Failed to resume job", job_id=job_id, error=str(e))
            raise SchedulerError(f"无法恢复任务 {job_id}: {e}")
    
    def get_jobs(self) -> List[dict]:
        """获取所有任务信息"""
        if self.scheduler is None:
            return []
        
        jobs = []
        for job in self.scheduler.get_jobs():
            job_info = {
                "id": job.id,
                "name": job.name,
                "func": job.func.__name__ if hasattr(job.func, '__name__') else str(job.func),
                "trigger": str(job.trigger),
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "pending": job.pending
            }
            
            # 添加自定义信息
            if job.id in self._jobs:
                job_info.update(self._jobs[job.id])
            
            jobs.append(job_info)
        
        return jobs
    
    async def _add_default_jobs(self) -> None:
        """添加默认任务"""
        try:
            # 添加每日定时任务（默认每天上午9点执行）
            await self.add_cron_job(
                job_id="daily_task_execution",
                func=self._execute_daily_tasks,
                cron_expression=self.settings.scheduler.default_schedule
            )
            
            # 添加系统健康检查任务（每5分钟执行一次）
            await self.add_interval_job(
                job_id="health_check",
                func=self._health_check,
                seconds=300  # 5分钟
            )
            
            self.logger.info("Default jobs added successfully")
            
        except Exception as e:
            self.logger.error("Failed to add default jobs", error=str(e))
    
    async def _execute_daily_tasks(self) -> None:
        """执行每日任务"""
        self.logger.info("Starting daily task execution")
        
        try:
            # 这里将调用任务管理器执行任务
            # TODO: 实现任务管理器后填充此逻辑
            self.logger.info("Daily tasks executed successfully")
            
        except Exception as e:
            self.logger.error("Failed to execute daily tasks", error=str(e))
    
    async def _health_check(self) -> None:
        """系统健康检查"""
        self.logger.debug("Performing health check")
        
        try:
            # 检查调度器状态
            if self.scheduler and self.scheduler.running:
                job_count = len(self.scheduler.get_jobs())
                self.logger.debug("Health check passed", active_jobs=job_count)
            else:
                self.logger.warning("Scheduler is not running")
                
        except Exception as e:
            self.logger.error("Health check failed", error=str(e)) 