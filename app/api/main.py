"""
FastAPI 主应用文件
包含基本的 API 路由和健康检查
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__, __description__
from app.config.settings import get_settings
from app.core.exceptions import AgentHubException
from app.core.logger import get_logger

# 获取配置和日志
settings = get_settings()
logger = get_logger("api")

# 创建 FastAPI 应用
app = FastAPI(
    title="AgentHub",
    description=__description__,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=settings.app.cors_allow_credentials,
    allow_methods=settings.app.cors_allow_methods,
    allow_headers=settings.app.cors_allow_headers,
)


@app.exception_handler(AgentHubException)
async def agenthub_exception_handler(request, exc: AgentHubException):
    """自定义异常处理器"""
    logger.error(
        "AgentHub exception occurred",
        error_code=exc.code,
        error_message=exc.message,
        error_details=exc.details,
        path=str(request.url)
    )
    
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """通用异常处理器"""
    logger.error(
        "Unexpected exception occurred",
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=str(request.url)
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": "INTERNAL_SERVER_ERROR",
            "message": "内部服务器错误",
            "details": {}
        }
    )


@app.get("/")
async def root() -> Dict[str, Any]:
    """根路径"""
    return {
        "message": "欢迎使用 AgentHub",
        "version": __version__,
        "description": __description__,
        "docs_url": "/docs",
        "health_url": "/health"
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """健康检查"""
    try:
        # 基本健康状态
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": __version__,
            "services": {}
        }
        
        # 检查各个服务状态
        # TODO: 在实现各服务后添加具体检查
        
        # 检查配置
        try:
            _ = get_settings()
            health_status["services"]["config"] = {"status": "healthy", "message": "配置加载正常"}
        except Exception as e:
            health_status["services"]["config"] = {"status": "unhealthy", "message": f"配置错误: {str(e)}"}
            health_status["status"] = "unhealthy"
        
        # 检查数据库（暂时跳过，数据库模块尚未实现）
        health_status["services"]["database"] = {"status": "not_implemented", "message": "数据库模块尚未实现"}
        
        # 检查调度器（暂时跳过，需要在启动时初始化）
        health_status["services"]["scheduler"] = {"status": "not_implemented", "message": "调度器未启动"}
        
        logger.info("Health check completed", status=health_status["status"])
        
        return health_status
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@app.get("/info")
async def app_info() -> Dict[str, Any]:
    """应用信息"""
    return {
        "name": settings.app.name,
        "version": __version__,
        "description": __description__,
        "debug": settings.app.debug,
        "timezone": settings.scheduler.timezone,
        "api_prefix": settings.app.api_prefix,
    }


# API 路由组
@app.get(f"{settings.app.api_prefix}/status")
async def api_status() -> Dict[str, Any]:
    """API 状态"""
    return {
        "api_version": "v1",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# 示例路由（后续会被实际的业务路由替换）
@app.get(f"{settings.app.api_prefix}/platforms")
async def list_platforms() -> Dict[str, Any]:
    """列出支持的平台"""
    return {
        "platforms": [
            {
                "name": "manus",
                "display_name": "Manus",
                "enabled": True,
                "status": "active"
            },
            {
                "name": "skywork", 
                "display_name": "Skywork",
                "enabled": True,
                "status": "active"
            },
            {
                "name": "coze_space",
                "display_name": "扣子空间",
                "enabled": True,
                "status": "active"
            }
        ]
    }


@app.get(f"{settings.app.api_prefix}/tasks")
async def list_tasks() -> Dict[str, Any]:
    """列出任务"""
    # TODO: 实现任务列表获取
    return {
        "tasks": [],
        "total": 0,
        "message": "任务管理功能尚未实现"
    }


@app.get(f"{settings.app.api_prefix}/topics") 
async def list_topics() -> Dict[str, Any]:
    """列出命题"""
    # TODO: 实现命题列表获取
    return {
        "topics": [],
        "total": 0,
        "message": "命题管理功能尚未实现"
    }


@app.get(f"{settings.app.api_prefix}/system/info")
async def system_info() -> Dict[str, Any]:
    """系统信息"""
    import psutil
    import platform
    from datetime import datetime
    
    try:
        # 获取系统基本信息
        system_info = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            },
            "resources": {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            },
            "application": {
                "name": settings.app.name,
                "version": __version__,
                "debug": settings.app.debug,
                "api_prefix": settings.app.api_prefix
            }
        }
        
        return system_info
        
    except Exception as e:
        logger.error("Failed to get system info", error=str(e))
        return {
            "error": True,
            "message": f"获取系统信息失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(
        "AgentHub API starting up",
        version=__version__,
        debug=settings.app.debug,
        api_prefix=settings.app.api_prefix
    )


# 关闭事件  
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("AgentHub API shutting down")


# 历史任务相关端点
@app.get(f"{settings.app.api_prefix}/history")
async def list_history_tasks(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """列出历史任务"""
    try:
        history_tasks = []
        stats = {"total": 0, "successful": 0, "failed": 0, "file_count": 0}
        
        # 扫描历史下载目录
        base_download_dir = Path("data/history_downloads")
        multi_platform_dir = Path("data/multi_platform_downloads")
        
        # 🔥 新增：扫描各平台特定的下载目录
        platform_specific_dirs = {
            "skywork": ["data/skywork_history", "data/skywork_downloads"],
            "manus": ["data/manus_history", "data/manus_downloads"],
            "coze_space": ["data/coze_space_history_downloads", "data/coze_downloads"]
        }
        
        # 扫描多平台下载目录
        if multi_platform_dir.exists():
            for session_dir in multi_platform_dir.glob("multi_platform_history_*"):
                for platform_dir in session_dir.iterdir():
                    if platform_dir.is_dir():
                        # 扫描平台目录下的所有任务目录
                        for task_dir in platform_dir.glob("task_*"):
                            if task_dir.is_dir():
                                task_data = await _load_task_data(task_dir, platform_dir.name)
                                if task_data:
                                    # 应用状态过滤
                                    if status and task_data.get("success") != (status == "success"):
                                        continue
                                    history_tasks.append(task_data)
        
        # 🔥 扫描各平台特定的下载目录
        for platform_name, dirs in platform_specific_dirs.items():
            # 如果指定了平台过滤，跳过其他平台
            if platform and platform != platform_name:
                continue
                
            for dir_path in dirs:
                platform_dir = Path(dir_path)
                if platform_dir.exists():
                    # 扫描下载会话目录（如 quick_xxx, batch_xxx 等）
                    for session_dir in platform_dir.iterdir():
                        if session_dir.is_dir():
                            # 检查是否是下载报告文件所在目录
                            download_report = session_dir / "download_report.json"
                            if download_report.exists():
                                # 从下载报告中加载任务
                                tasks_from_report = await _load_tasks_from_download_report(download_report, platform_name)
                                for task_data in tasks_from_report:
                                    if status and task_data.get("success") != (status == "success"):
                                        continue
                                    history_tasks.append(task_data)
                            else:
                                # 直接扫描任务目录
                                for task_dir in session_dir.glob("task_*"):
                                    if task_dir.is_dir():
                                        task_data = await _load_task_data(task_dir, platform_name)
                                        if task_data:
                                            if status and task_data.get("success") != (status == "success"):
                                                continue
                                            history_tasks.append(task_data)
        
        # 单平台下载目录
        if base_download_dir.exists():
            for task_dir in base_download_dir.glob("task_*"):
                if task_dir.is_dir():
                    # 🔥 修复：从metadata中读取正确的平台信息
                    detected_platform = await _detect_platform_from_metadata(task_dir)
                    task_data = await _load_task_data(task_dir, detected_platform)
                    if task_data:
                        if platform and task_data.get("platform") != platform:
                            continue
                        if status and task_data.get("success") != (status == "success"):
                            continue
                        history_tasks.append(task_data)
        
        # 去重处理
        history_tasks = _deduplicate_tasks(history_tasks)
        
        # 更新统计信息
        for task in history_tasks:
            stats["total"] += 1
            if task.get("success"):
                stats["successful"] += 1
            else:
                stats["failed"] += 1
            stats["file_count"] += task.get("files_count", 0)
        
        # 排序
        history_tasks.sort(key=lambda x: x.get("download_time", ""), reverse=True)
        
        # 分页
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_tasks = history_tasks[start_idx:end_idx]
        
        return {
            "tasks": paginated_tasks,
            "stats": stats,
            "pagination": {
                "page": page,
                "size": size,
                "total": len(history_tasks),
                "pages": (len(history_tasks) + size - 1) // size
            }
        }
        
    except Exception as e:
        logger.error(f"列出历史任务失败: {e}")
        return {
            "tasks": [],
            "stats": {"total": 0, "successful": 0, "failed": 0, "file_count": 0},
            "error": str(e)
        }

@app.get(f"{settings.app.api_prefix}/history/{{task_id}}")
async def get_history_task_detail(task_id: str) -> Dict[str, Any]:
    """获取历史任务详情"""
    try:
        # 查找任务目录
        task_dir = await _find_task_directory(task_id)
        if not task_dir:
            return {"error": "任务不存在"}
        
        # 加载任务详情
        task_detail = await _load_task_detail(task_dir)
        return task_detail
        
    except Exception as e:
        logger.error(f"获取任务详情失败: {e}")
        return {"error": str(e)}

@app.get(f"{settings.app.api_prefix}/history/file/{{task_id}}/{{filename}}")
async def download_history_file(task_id: str, filename: str):
    """下载历史任务文件"""
    try:
        from fastapi.responses import FileResponse
        
        # 查找任务目录
        task_dir = await _find_task_directory(task_id)
        if not task_dir:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 查找文件
        file_path = task_dir / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"下载文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get(f"{settings.app.api_prefix}/history/download/{{task_id}}")
async def download_task_archive(task_id: str):
    """下载任务打包文件"""
    try:
        import zipfile
        import tempfile
        from fastapi.responses import FileResponse
        
        # 查找任务目录
        task_dir = await _find_task_directory(task_id)
        if not task_dir:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 创建临时zip文件
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            zip_path = tmp_file.name
        
        # 打包任务文件
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in task_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(task_dir)
                    zipf.write(file_path, arcname)
        
        return FileResponse(
            path=zip_path,
            filename=f"{task_id}.zip",
            media_type='application/zip'
        )
        
    except Exception as e:
        logger.error(f"下载任务打包失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.app.api_prefix}/history/batch-download")
async def batch_download_tasks(request: Dict[str, List[str]]) -> Dict[str, Any]:
    """批量下载任务"""
    try:
        import zipfile
        import tempfile
        from fastapi.responses import FileResponse
        
        task_ids = request.get("task_ids", [])
        if not task_ids:
            raise HTTPException(status_code=400, detail="未指定任务ID")
        
        # 创建临时zip文件
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            zip_path = tmp_file.name
        
        successful_tasks = []
        failed_tasks = []
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for task_id in task_ids:
                try:
                    task_dir = await _find_task_directory(task_id)
                    if task_dir and task_dir.exists():
                        # 添加任务文件到zip
                        for file_path in task_dir.rglob('*'):
                            if file_path.is_file():
                                arcname = f"{task_id}/{file_path.relative_to(task_dir)}"
                                zipf.write(file_path, arcname)
                        successful_tasks.append(task_id)
                    else:
                        failed_tasks.append(task_id)
                except Exception:
                    failed_tasks.append(task_id)
        
        return FileResponse(
            path=zip_path,
            filename=f"batch_download_{int(time.time())}.zip",
            media_type='application/zip'
        )
        
    except Exception as e:
        logger.error(f"批量下载失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete(f"{settings.app.api_prefix}/history/{{task_id}}")
async def delete_history_task(task_id: str) -> Dict[str, Any]:
    """删除历史任务"""
    try:
        import shutil
        
        # 查找任务目录
        task_dir = await _find_task_directory(task_id)
        if not task_dir:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 删除任务目录
        shutil.rmtree(task_dir)
        
        return {"message": "任务删除成功"}
        
    except Exception as e:
        logger.error(f"删除任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.app.api_prefix}/history/batch-delete")
async def batch_delete_tasks(request: Dict[str, List[str]]) -> Dict[str, Any]:
    """批量删除任务"""
    try:
        import shutil
        
        task_ids = request.get("task_ids", [])
        if not task_ids:
            raise HTTPException(status_code=400, detail="未指定任务ID")
        
        successful_deletes = []
        failed_deletes = []
        
        for task_id in task_ids:
            try:
                task_dir = await _find_task_directory(task_id)
                if task_dir and task_dir.exists():
                    shutil.rmtree(task_dir)
                    successful_deletes.append(task_id)
                else:
                    failed_deletes.append(task_id)
            except Exception:
                failed_deletes.append(task_id)
        
        return {
            "message": f"成功删除 {len(successful_deletes)} 个任务",
            "successful": successful_deletes,
            "failed": failed_deletes
        }
        
    except Exception as e:
        logger.error(f"批量删除失败: {e}")
        return {"error": str(e)}


@app.post(f"{settings.app.api_prefix}/history/{{task_id}}/ai-summary")
async def generate_task_ai_summary(task_id: str) -> Dict[str, Any]:
    """为指定任务生成AI智能总结"""
    try:
        from app.core.task_summary_generator import generate_task_summary
        
        # 查找任务目录
        task_dir = await _find_task_directory(task_id)
        if not task_dir or not task_dir.exists():
            raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
        
        logger.info(
            "开始生成任务AI总结",
            task_id=task_id,
            task_dir=str(task_dir)
        )
        
        # 获取任务标题
        task_data = await _load_task_detail(task_dir)
        task_title = task_data.get("task", {}).get("title", "未知任务")
        
        # 使用任务总结生成器
        result = await generate_task_summary(task_dir, task_title, force=True)
        
        if result["success"]:
            logger.info(
                "任务AI总结生成成功",
                task_id=task_id,
                analysis_type=result.get("analysis_type", "unknown")
            )
            
            return {
                "success": True,
                "summary": result["summary"],
                "cached": False  # 新生成的总结
            }
        else:
            logger.warning("AI总结生成失败", task_id=task_id, error=result.get("error"))
            return {
                "success": False,
                "error": result.get("error", "总结生成失败"),
                "summary": None
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("生成AI总结失败", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"生成AI总结失败: {str(e)}")


@app.get(f"{settings.app.api_prefix}/history/{{task_id}}/ai-summary")
async def get_task_ai_summary(task_id: str) -> Dict[str, Any]:
    """获取任务的AI智能总结（缓存版本）"""
    try:
        from app.core.task_summary_generator import get_task_summary
        
        # 查找任务目录
        task_dir = await _find_task_directory(task_id)
        if not task_dir or not task_dir.exists():
            raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
        
        # 获取已有总结
        summary_data = get_task_summary(task_dir)
        
        if summary_data:
            logger.info("返回缓存的AI总结", task_id=task_id)
            return {
                "success": True,
                "summary": summary_data,
                "cached": True  # 来自缓存
            }
        
        # 如果没有缓存，返回需要生成的状态
        return {
            "success": False,
            "error": "AI总结尚未生成，请先调用生成接口",
            "summary": None,
            "cached": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取AI总结失败", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"获取AI总结失败: {str(e)}")

# 辅助函数
async def _detect_platform_from_metadata(task_dir: Path) -> str:
    """从任务元数据中检测平台信息"""
    try:
        metadata_file = task_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 优先从download信息中获取平台
            download_platform = metadata.get("download", {}).get("platform", "")
            if download_platform:
                return download_platform
            
            # 从任务ID中推断平台
            task_id = metadata.get("task", {}).get("id", "")
            if task_id:
                if "skywork" in task_id.lower():
                    return "skywork"
                elif "manus" in task_id.lower():
                    return "manus"
                elif "chatgpt" in task_id.lower():
                    return "chatgpt"
            
            # 从页面URL推断平台
            page_url = metadata.get("download", {}).get("page_url", "")
            if page_url:
                if "skywork.ai" in page_url:
                    return "skywork"
                elif "manus.im" in page_url or "manus.ai" in page_url:
                    return "manus"
                elif "openai.com" in page_url or "chatgpt.com" in page_url:
                    return "chatgpt"
        
        # 从目录名推断平台
        task_dir_name = task_dir.name
        if "skywork" in task_dir_name.lower():
            return "skywork"
        elif "manus" in task_dir_name.lower():
            return "manus"
        elif "chatgpt" in task_dir_name.lower():
            return "chatgpt"
        
        return "unknown"
        
    except Exception as e:
        logger.error(f"检测平台信息失败: {e}")
        return "unknown"

async def _load_task_data(task_dir: Path, platform: str) -> Optional[Dict[str, Any]]:
    """加载任务数据"""
    try:
        metadata_file = task_dir / "metadata.json"
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 统计文件数量
        file_count = len(list(task_dir.glob('*')))
        
        # 读取内容文件
        content_file = task_dir / "content.txt"
        content_preview = ""
        if content_file.exists():
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取内容预览（跳过元数据行）
                lines = content.split('\n')
                content_start = 0
                for i, line in enumerate(lines):
                    if line.startswith('=='):
                        content_start = i + 1
                        break
                if content_start < len(lines):
                    content_preview = '\n'.join(lines[content_start:content_start+3])[:200]
        
        task_info = metadata.get("task", {})
        download_info = metadata.get("download", {})
        
        title = task_info.get("title", "未知任务")
        
        # 过滤无效的任务标题
        if _is_invalid_task_title(title):
            return None
        
        # 🔥 对扣子空间的标题进行智能清理
        display_title = title
        if platform == "coze_space":
            display_title = _extract_coze_smart_core(title)
            if not display_title or len(display_title) < 3:
                display_title = _clean_coze_title_core(title)
            if not display_title:
                display_title = title  # 回退到原标题
        
        return {
            "id": task_info.get("id"),
            "title": display_title,
            "platform": platform,
            "success": file_count > 1,  # 如果有多个文件说明下载成功
            "files_count": file_count,
            "content_preview": content_preview,
            "download_time": download_info.get("timestamp"),
            "download_dir": str(task_dir),
            "task_date": task_info.get("date"),
            "task_url": task_info.get("url"),
            "page_url": download_info.get("page_url"),
            "page_title": download_info.get("page_title"),
            "content_length": download_info.get("content_length", 0)
        }
        
    except Exception as e:
        logger.error(f"加载任务数据失败: {e}")
        return None

async def _find_task_directory(task_id: str) -> Optional[Path]:
    """查找任务目录"""
    try:
        # 🔥 扩展搜索范围：包含各平台特定的下载目录
        search_dirs = [
            "data/history_downloads",
            "data/multi_platform_downloads",
            "data/skywork_history", 
            "data/skywork_downloads",
            "data/manus_history",
            "data/manus_downloads", 
            "data/coze_space_history_downloads",
            "data/coze_downloads"
        ]
        
        # 在多平台下载目录中查找
        multi_platform_dir = Path("data/multi_platform_downloads")
        if multi_platform_dir.exists():
            for session_dir in multi_platform_dir.glob("multi_platform_history_*"):
                for platform_dir in session_dir.iterdir():
                    if platform_dir.is_dir():
                        task_dir = platform_dir / f"task_{task_id}"
                        if task_dir.exists():
                            return task_dir
        
        # 在各平台特定目录中查找
        for dir_path in search_dirs:
            base_dir = Path(dir_path)
            if base_dir.exists():
                # 直接查找任务目录
                task_dir = base_dir / f"task_{task_id}"
                if task_dir.exists():
                    return task_dir
                
                # 在下载会话目录中查找
                for session_dir in base_dir.iterdir():
                    if session_dir.is_dir():
                        task_dir = session_dir / f"task_{task_id}"
                        if task_dir.exists():
                            return task_dir
                        
                        # 还可能是直接包含任务ID的目录
                        if task_id in session_dir.name:
                            return session_dir
        
        return None
        
    except Exception as e:
        logger.error(f"查找任务目录失败: {e}")
        return None

async def _load_task_detail(task_dir: Path) -> Dict[str, Any]:
    """加载任务详细信息"""
    try:
        # 加载元数据
        metadata_file = task_dir / "metadata.json"
        metadata = {}
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        # 扫描所有文件
        files = []
        for file_path in task_dir.glob('*'):
            if file_path.is_file():
                file_info = {
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "type": _get_file_type(file_path),
                }
                
                # 如果是文本文件，读取内容
                if file_info["type"] in ["text", "json", "html"]:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            file_info["content"] = content
                    except:
                        file_info["content"] = "无法读取文件内容"
                
                files.append(file_info)
        
        return {
            "task": metadata.get("task", {}),
            "download": metadata.get("download", {}),
            "files": files,
            "task_dir": str(task_dir)
        }
        
    except Exception as e:
        logger.error(f"加载任务详情失败: {e}")
        return {"error": str(e)}

def _get_file_type(file_path: Path) -> str:
    """根据文件扩展名确定文件类型"""
    suffix = file_path.suffix.lower()
    
    type_map = {
        '.txt': 'text',
        '.json': 'json',
        '.html': 'html',
        '.htm': 'html',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.gif': 'image',
        '.pdf': 'pdf',
        '.doc': 'document',
        '.docx': 'document',
        '.xls': 'spreadsheet',
        '.xlsx': 'spreadsheet'
    }
    
    return type_map.get(suffix, 'binary')

async def _load_tasks_from_download_report(report_path: Path, platform: str) -> List[Dict[str, Any]]:
    """从下载报告中加载任务数据"""
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        tasks = []
        results = report_data.get("results", [])
        download_time = report_data.get("download_time", "")
        
        # 用于扣子空间智能去重的集合
        seen_smart_cores = set()
        
        for result in results:
            try:
                # 基本任务信息
                task_id = result.get("task_id", "")
                title = result.get("title", "未知任务")
                
                # 🔥 扣子空间专用智能去重
                if platform == "coze_space":
                    smart_core = _extract_coze_smart_core(title)
                    if smart_core in seen_smart_cores:
                        logger.debug(f"跳过重复任务: {title[:60]}...")
                        continue
                    seen_smart_cores.add(smart_core)
                else:
                    # 其他平台的原有去重逻辑
                    clean_title = _clean_task_title_for_dedup(title)
                    if clean_title in seen_smart_cores:
                        logger.debug(f"跳过重复任务: {title}")
                        continue
                    seen_smart_cores.add(clean_title)
                
                # 🔥 对扣子空间的标题进行智能清理
                display_title = title
                if platform == "coze_space":
                    display_title = _extract_coze_smart_core(title)
                    if not display_title or len(display_title) < 3:
                        display_title = _clean_coze_title_core(title)
                    if not display_title:
                        display_title = title  # 回退到原标题
                
                task_data = {
                    "id": task_id,
                    "title": display_title,
                    "platform": platform,
                    "success": result.get("success", False),
                    "download_time": download_time,
                    "files_count": len(result.get("files", [])),
                    "download_dir": result.get("download_dir", ""),
                    "content_preview": display_title[:200] + "..." if len(display_title) > 200 else display_title
                }
                
                # 如果有下载目录，尝试获取更多信息
                if task_data["download_dir"]:
                    task_dir = Path(task_data["download_dir"])
                    if task_dir.exists():
                        # 查找并读取metadata
                        metadata_file = task_dir / "metadata.json"
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r', encoding='utf-8') as f:
                                    metadata = json.load(f)
                                    
                                # 支持新的标准化格式
                                if "task" in metadata:
                                    task_info = metadata["task"]
                                    download_info = metadata.get("download", {})
                                    
                                    task_data.update({
                                        "task_url": task_info.get("url", ""),
                                        "task_date": task_info.get("date", ""),
                                        "page_title": task_info.get("title", task_data["title"]),
                                        "page_url": task_info.get("url", ""),
                                        "content_length": len(task_info.get("preview", "")),
                                        "timestamp": download_info.get("timestamp", download_time)
                                    })
                                else:
                                    # 兼容旧格式
                                    task_data.update({
                                        "task_url": metadata.get("url", ""),
                                        "page_title": metadata.get("title", task_data["title"]),
                                        "page_url": metadata.get("url", ""),
                                        "content_length": len(metadata.get("preview", "")),
                                        "timestamp": metadata.get("timestamp", download_time)
                                    })
                                    
                            except Exception as e:
                                logger.warning(f"读取metadata失败: {e}")
                
                # 最终检查任务是否有效
                if not _is_invalid_task_title(task_data["title"]):
                    tasks.append(task_data)
                
            except Exception as e:
                logger.warning(f"解析任务结果失败: {e}")
                continue
        
        logger.info(f"从下载报告加载了 {len(tasks)} 个有效任务（去重后）")
        return tasks
        
    except Exception as e:
        logger.error(f"读取下载报告失败: {e}")
        return []

def _deduplicate_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """去除重复任务"""
    if not tasks:
        return tasks
    
    # 用于跟踪已见过的任务
    seen_tasks = {}
    deduplicated = []
    
    for task in tasks:
        # 生成去重键
        dedup_key = _generate_dedup_key(task)
        
        if dedup_key not in seen_tasks:
            # 这是一个新任务
            seen_tasks[dedup_key] = task
            deduplicated.append(task)
        else:
            # 这是重复任务，选择更好的版本
            existing_task = seen_tasks[dedup_key]
            better_task = _choose_better_task(existing_task, task)
            
            if better_task != existing_task:
                # 替换为更好的任务
                seen_tasks[dedup_key] = better_task
                # 在列表中找到并替换
                for i, t in enumerate(deduplicated):
                    if t == existing_task:
                        deduplicated[i] = better_task
                        break
    
    return deduplicated

def _generate_dedup_key(task: Dict[str, Any]) -> str:
    """生成任务去重键（增强版）"""
    platform = task.get("platform", "unknown")
    task_id = task.get("id", "")
    title = task.get("title", "").strip()
    download_time = task.get("download_time", "")
    
    # 🔥 扣子空间专用的强化去重逻辑
    if platform == "coze_space":
        return _generate_coze_dedup_key(task)
    
    # 其他平台的原有逻辑
    # 1. 基于任务ID进行去重（最精确的标识）
    if task_id and task_id.strip() and not _is_auto_generated_id(task_id, platform):
        return f"{platform}:id:{task_id}"
    
    # 2. 基于页面URL进行去重
    page_url = task.get("page_url", "")
    if page_url and page_url not in ["https://manus.im/app", "https://space.coze.cn/", ""]:
        return f"{platform}:url:{page_url}"
    
    # 3. 基于标题进行去重
    clean_title = _clean_title_for_dedup(title)
    if clean_title and len(clean_title) >= 5:
        time_part = download_time[:16] if download_time else "no_time"
        return f"{platform}:title:{clean_title}:time:{time_part}"
    
    # 4. 最后备用方案
    content_length = task.get("content_length", 0)
    time_part = download_time[:16] if download_time else "no_time"
    return f"{platform}:fallback:{title[:20]}:length:{content_length}:time:{time_part}"

def _generate_coze_dedup_key(task: Dict[str, Any]) -> str:
    """扣子空间专用去重键生成"""
    title = task.get("title", "").strip()
    task_id = task.get("id", "")
    content_preview = task.get("content_preview", "")
    
    # 🔥 智能标题清理：处理超长标题和多任务合并的情况
    clean_core = _extract_coze_smart_core(title)
    
    # 🔥 使用内容特征辅助去重
    content_hash = ""
    if content_preview and len(content_preview) > 20:
        import hashlib
        content_hash = hashlib.md5(content_preview.encode('utf-8')).hexdigest()[:8]
    
    # 🔥 组合去重键：核心标题 + 内容哈希
    if clean_core and content_hash:
        return f"coze_space:smart:{clean_core}:{content_hash}"
    elif clean_core:
        return f"coze_space:smart:{clean_core}"
    else:
        # 备用方案
        session_id = _extract_session_id_from_task_id(task_id)
        return f"coze_space:fallback:{title[:30]}:session:{session_id}"

def _extract_coze_smart_core(title: str) -> str:
    """智能提取扣子空间标题核心"""
    if not title:
        return ""
    
    import re
    
    # 🔥 处理超长标题：可能是多个任务拼接的
    if len(title) > 80:
        # 更精确的模式匹配，优先提取第一个完整主题
        patterns = [
            # 匹配 "过去N天 主题 状态标记" 格式
            r'(?:过去\d+天\s+)?([^一轮任务完成任务已结束]{4,40}?)(?:\s+一轮任务完成|\s+任务已结束)',
            # 匹配 "过往 主题 状态标记" 格式
            r'(?:过往\s+)?([^一轮任务完成任务已结束]{4,40}?)(?:\s+一轮任务完成|\s+任务已结束)',
            # 匹配开头的主题（直到第一个状态词或时间前缀）
            r'^([^一轮任务完成任务已结束\s]{4,40}?)(?:\s+过去\d+天|\s+过往|\s+一轮任务完成|\s+任务已结束)',
            # 匹配开头到第一个空格的主题
            r'^([^\s]{3,30}?)(?=\s)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, title)
            if matches:
                core = matches[0].strip()
                
                # 清理提取的核心内容
                # 移除时间前缀
                time_prefixes = ['过去', '过往', '新任务', '最近']
                for prefix in time_prefixes:
                    if core.startswith(prefix):
                        # 找到数字后的部分
                        remaining = re.sub(r'^' + prefix + r'\d*[天月]?\s*', '', core)
                        if len(remaining) >= 3:
                            core = remaining
                        break
                
                # 进一步清理
                core = _clean_coze_title_core(core)
                if len(core) >= 3:
                    return core[:40]
    
    # 🔥 处理正常长度标题 - 直接清理
    clean = _clean_coze_title_core(title)
    
    # 🔥 如果清理后仍然很长，按意义单元截取
    if len(clean) > 40:
        # 按常见分隔符和语义单元分割
        parts = re.split(r'[，。；：\s]+', clean)
        
        # 选择最有意义的前几个部分
        meaningful_parts = []
        total_length = 0
        
        for part in parts:
            part = part.strip()
            if len(part) >= 2:  # 至少2个字符
                # 过滤掉明显的噪音词汇
                if part not in ['过去', '过往', '新任务', '最近', '天', '个月', '年', '一轮', '任务', '完成', '已结束']:
                    if total_length + len(part) <= 35:  # 控制总长度
                        meaningful_parts.append(part)
                        total_length += len(part)
                    else:
                        break
        
        if meaningful_parts:
            clean = ' '.join(meaningful_parts)
    
    return clean[:40] if clean else ""

def _clean_coze_title_core(title: str) -> str:
    """清理扣子空间标题核心"""
    if not title:
        return ""
    
    clean = title.strip()
    
    # 移除状态标记
    status_markers = [
        "一轮任务完成", "任务已结束", "任务已完成", 
        "任务完成", "下载完成", "处理完成"
    ]
    for marker in status_markers:
        clean = clean.replace(marker, "")
    
    # 改进的时间前缀移除 - 支持多种模式
    import re
    
    # 🔥 更强力的时间前缀清理
    # 移除开头的时间前缀（更精确的匹配）
    time_patterns = [
        r'^过去\d+天\s*',      # 过去7天、过去30天
        r'^过往\s*',          # 过往
        r'^新任务\s*',        # 新任务  
        r'^最近\s*',          # 最近
        r'^历史\s*',          # 历史
        r'^过去\d+个月\s*',    # 过去3个月
        r'^上个月\s*',        # 上个月
        r'^本月\s*',          # 本月
    ]
    
    for pattern in time_patterns:
        clean = re.sub(pattern, '', clean, flags=re.IGNORECASE)
    
    # 移除中间出现的时间前缀（对于连接的标题）
    middle_time_patterns = [
        r'\s+过去\d+天\s+',
        r'\s+过去\d+个月\s+',
        r'\s+过往\s+',
        r'\s+新任务\s+',
        r'\s+最近\s+',
        r'\s+上个月\s+',
        r'\s+本月\s+',
    ]
    
    for pattern in middle_time_patterns:
        clean = re.sub(pattern, ' ', clean, flags=re.IGNORECASE)
    
    # 🔥 再次移除开头的时间前缀（处理清理后露出的前缀）
    for pattern in time_patterns:
        clean = re.sub(pattern, '', clean, flags=re.IGNORECASE)
    
    # 移除AI回复标识
    ai_prefixes = ["我已完成", "我已为您", "感谢您的反馈", "根据您的要求"]
    for prefix in ai_prefixes:
        if clean.startswith(prefix):
            clean = clean[len(prefix):].strip()
    
    # 清理多余的空格和标点符号
    clean = re.sub(r'\s+', ' ', clean).strip()
    clean = clean.strip("，。！？、 ：；")
    
    # 🔥 如果清理后仍然很长，截取前面的有意义部分
    if len(clean) > 50:
        # 按常见分隔符分割，找到第一个完整的主题
        parts = re.split(r'[，。；：\s]+', clean)
        meaningful_parts = []
        total_length = 0
        
        for part in parts:
            if len(part) >= 2:  # 至少2个字符的有意义部分
                if total_length + len(part) <= 40:  # 控制总长度
                    meaningful_parts.append(part)
                    total_length += len(part)
                else:
                    break
        
        if meaningful_parts:
            clean = ' '.join(meaningful_parts)
    
    # 如果清理后太短，尝试提取第一个有意义的片段
    if len(clean) < 3 and title:
        # 从原标题中提取第一个有意义的词组
        words = re.split(r'[^\w\u4e00-\u9fff]+', title)
        meaningful_words = [w for w in words if len(w) >= 2 and w not in ['过去', '天', '过往', '新任务', '最近', '一轮', '任务', '完成', '已结束', '个月']]
        if meaningful_words:
            clean = ' '.join(meaningful_words[:3])  # 取前3个有意义的词
    
    return clean

def _is_auto_generated_id(task_id: str, platform: str) -> bool:
    """检查任务ID是否是自动生成的索引"""
    if platform == "coze_space":
        # 扣子空间的ID格式: coze_space_history_N_timestamp
        import re
        pattern = r"coze_space_history_\d+_\d+"
        return bool(re.match(pattern, task_id))
    return False

def _clean_task_title_for_dedup(title: str) -> str:
    """清理任务标题用于去重比较"""
    if not title:
        return ""
    
    # 移除状态关键词
    status_words = ["一轮任务完成", "任务已结束", "任务已完成", "下载失败"]
    clean = title
    for word in status_words:
        clean = clean.replace(word, "")
    
    # 移除时间前缀
    time_prefixes = ["过去7天", "过去30天", "过往", "新任务"]
    for prefix in time_prefixes:
        clean = clean.replace(prefix, "")
    
    # 清理空格并转换为小写
    return " ".join(clean.split()).strip().lower()

def _is_invalid_task_title(title: str) -> bool:
    """检查任务标题是否无效"""
    if not title or title.strip() == "":
        return True
    
    # 检查是否只包含状态信息
    status_only_patterns = ["未知任务", "下载失败", "无标题", "无效任务"]
    clean_title = title.strip().lower()
    
    return any(pattern in clean_title for pattern in status_only_patterns)

def _extract_session_id_from_task_id(task_id: str) -> str:
    """从任务ID中提取会话ID"""
    if "_" in task_id:
        # 对于格式如 coze_space_history_0_1748783734，提取最后的时间戳部分
        parts = task_id.split("_")
        if len(parts) >= 2:
            return parts[-1]  # 返回时间戳部分
    return "unknown"

def _extract_coze_core_content(title: str) -> str:
    """提取扣子空间标题的核心内容"""
    if not title:
        return ""
    
    # 移除扣子空间特有的前缀和后缀
    content = title
    
    # 移除常见的前缀
    prefixes_to_remove = [
        "新任务 ",
        "过去7天 ",
        "过去30天 ",
        "过往 "
    ]
    
    for prefix in prefixes_to_remove:
        if content.startswith(prefix):
            content = content[len(prefix):]
    
    # 查找第一个有意义的主题
    # 按空格或常见分隔符分割
    import re
    
    # 查找第一个实质性的主题（通常在前50个字符内）
    meaningful_parts = []
    parts = re.split(r'[，。\s]+', content)
    
    for part in parts:
        if len(part) >= 3 and not part in ["一轮任务完成", "任务已结束", "搜"]:
            meaningful_parts.append(part)
        if len(meaningful_parts) >= 2:  # 取前两个有意义的部分
            break
    
    if meaningful_parts:
        core = " ".join(meaningful_parts[:2])  # 取前两个部分
        # 限制长度
        return core[:50].strip()
    
    # 如果找不到有意义的部分，返回前30个字符
    return content[:30].strip()

def _clean_title_for_dedup(title: str) -> str:
    """清理标题用于去重"""
    if not title:
        return ""
    
    # 检查是否是通用问候语或无意义标题
    greeting_patterns = [
        "你好，",
        "您好，", 
        "我能为你做什么",
        "我能为您做什么",
        "有什么可以帮助",
        "请问需要什么帮助",
        "感谢您使用"
    ]
    
    for pattern in greeting_patterns:
        if pattern in title:
            return ""  # 返回空字符串，表示这是无效标题
    
    # 移除常见的AI回复前缀
    prefixes_to_remove = [
        "我已完成对",
        "我已为您",
        "感谢您的反馈！",
        "你好，",
        "您好，",
        "我明白了，"
    ]
    
    clean_title = title
    for prefix in prefixes_to_remove:
        if clean_title.startswith(prefix):
            # 尝试提取真正的主题
            remaining = clean_title[len(prefix):].strip()
            
            # 查找核心主题的结束点
            end_patterns = [
                "的全面分析",
                "的详细分析", 
                "的分析报告",
                "的研究报告",
                "分析报告",
                "功能特点",
                "最新版本",
                "。",
                "，"
            ]
            
            for pattern in end_patterns:
                if pattern in remaining:
                    pattern_index = remaining.find(pattern)
                    if 0 < pattern_index < 50:  # 合理的长度范围
                        clean_title = remaining[:pattern_index].strip()
                        break
            else:
                # 如果没找到结束模式，取前30个字符
                clean_title = remaining[:30].strip()
            break
    
    # 进一步清理标题
    clean_title = clean_title.strip("，。！？、 ")
    
    # 移除版本号和时间信息的影响
    import re
    clean_title = re.sub(r'\s+R\d+.*$', '', clean_title)  # 移除 R1, R2 等版本号
    clean_title = re.sub(r'\s+\d{4}年.*$', '', clean_title)  # 移除年份信息
    clean_title = re.sub(r'\s+最新.*$', '', clean_title)  # 移除"最新"相关后缀
    
    return clean_title.strip()

def _choose_better_task(task1: Dict[str, Any], task2: Dict[str, Any]) -> Dict[str, Any]:
    """在两个重复任务中选择更好的一个"""
    
    # 优先选择标题更简洁的任务
    title1 = task1.get("title", "")
    title2 = task2.get("title", "")
    
    # 计算标题质量分数（越低越好）
    score1 = _calculate_title_quality_score(title1)
    score2 = _calculate_title_quality_score(title2)
    
    if score1 != score2:
        return task1 if score1 < score2 else task2
    
    # 如果标题质量相同，优先选择下载时间更晚的（更新的版本）
    time1 = task1.get("download_time", "")
    time2 = task2.get("download_time", "")
    
    if time1 and time2:
        return task2 if time2 > time1 else task1
    
    # 默认选择第一个
    return task1

def _calculate_title_quality_score(title: str) -> int:
    """计算标题质量分数（越低越好）"""
    if not title:
        return 1000
    
    score = 0
    
    # 长度惩罚：过长的标题得分更高
    if len(title) > 30:
        score += (len(title) - 30) * 2
    
    # 检查是否包含AI回复特征
    ai_phrases = [
        "我已完成", "我已为您", "感谢您的反馈", "我明白了",
        "根据您的要求", "为您提供", "分析报告", "详细的"
    ]
    
    for phrase in ai_phrases:
        if phrase in title:
            score += 50  # 重大惩罚
    
    # 检查是否包含过多的标点符号
    punct_count = sum(1 for c in title if c in "，。！？、")
    if punct_count > 3:
        score += punct_count * 10
    
    # 奖励简洁明确的标题
    if 5 <= len(title) <= 25 and not any(phrase in title for phrase in ai_phrases):
        score -= 20
    
    return score

def _is_invalid_task_title(title: str) -> bool:
    """判断任务标题是否无效"""
    if not title or title.strip() == "":
        return True
    
    # 过滤过长的标题（超过100个字符的很可能是回复内容）
    if len(title) > 100:
        return True
    
    # 过滤问候语
    greeting_patterns = [
        "你好，",
        "您好，", 
        "我能为你做什么",
        "我能为您做什么",
        "有什么可以帮助",
        "请问需要什么帮助",
        "感谢您使用"
    ]
    
    for pattern in greeting_patterns:
        if pattern in title:
            return True
    
    # 过滤明显的AI回复内容
    ai_reply_patterns = [
        "感谢您的反馈！",
        "我明白了，您希望",
        "根据您的要求",
        "我会为您",
        "我将为您",
        "现在为您提供",
        "我已经为您",
        "稍后我会"
    ]
    
    for pattern in ai_reply_patterns:
        if pattern in title:
            return True
    
    # 过滤包含太多标点符号的标题
    punct_count = sum(1 for c in title if c in "，。！？、；：""''（）【】")
    if punct_count > len(title) * 0.2:  # 标点符号超过20%
        return True
    
    # 过滤只包含特殊字符或数字的标题
    if title.replace(' ', '').replace('\n', '').replace('\t', '') == "":
        return True
    
    return False



if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 