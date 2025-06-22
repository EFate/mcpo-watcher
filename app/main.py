import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import Dict, Any

from . import models, validator, controller, watcher

# [新增] 创建一个全局的异步锁，用于防止竞争条件
config_change_lock = asyncio.Lock()

# 应用状态变量
app_state: Dict[str, Any] = {
    "status": "initializing",
    "message": "Application is starting up.",
    "last_config": None
}

async def handle_config_change():
    """核心处理流程：加载 -> 验证 -> 重启。"""
    
    # 使用 "async with" 语法来获取锁。
    # 如果锁已被占用，当前任务会在此等待，直到锁被释放。
    # 这可以保证无论文件变化事件触发多快、多少次，重启逻辑都将按顺序执行。
    async with config_change_lock:
        
        print("--- Locked: Starting config change handling ---")
        
        # 1. 加载配置
        config = models.load_config()
        if not config:
            app_state["status"] = "error"
            app_state["message"] = "Failed to load or parse config.json. Check logs."
            print("--- Unlocked: Aborted due to config load failure ---")
            return

        app_state["last_config"] = config.model_dump(by_alias=True)
        
        # 2. 验证服务
        is_valid, message = await validator.validate_all_services(config)
        if not is_valid:
            app_state["status"] = "error"
            app_state["message"] = f"Service validation failed: {message}"
            print(f"Configuration change aborted. Reason: {message}")
            print("--- Unlocked: Aborted due to validation failure ---")
            return

        # 3. 重启 MCPO
        print("All services validated. Restarting MCPO process...")
        await controller.restart_mcpo()

        if controller.mcpo_process and controller.mcpo_process.returncode is None:
            app_state["status"] = "running"
            app_state["message"] = f"MCPO restarted successfully (PID: {controller.mcpo_process.pid})."
        else:
            app_state["status"] = "error"
            app_state["message"] = "Failed to start MCPO process after restart. Check logs."
        
        print(app_state["message"])
        print("--- Unlocked: Finished config change handling ---")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI应用的生命周期管理器。"""
    print("Application starting up...")
    
    # 启动文件监控器
    loop = asyncio.get_running_loop()
    observer = watcher.start_watching(".", loop, handle_config_change)
    app.state.observer = observer
    
    # 执行首次配置加载和MCPO启动
    await handle_config_change()
    
    print("Startup complete. Application is ready.")
    
    yield
    
    print("Application shutting down...")
    
    # 停止文件监控
    if hasattr(app.state, 'observer') and app.state.observer.is_alive():
        app.state.observer.stop()
        app.state.observer.join()
        print("File watcher stopped.")
    
    # 停止mcpo子进程
    await controller.stop_mcpo()
    print("Shutdown complete.")


# 初始化FastAPI应用
app = FastAPI(title="MCPO Config Monitor", version="2.0", lifespan=lifespan)

@app.get("/status", tags=["Monitoring"])
async def get_status():
    """提供API端点来查询应用的实时状态。"""
    # 为了线程安全，在读取时也加上锁
    async with config_change_lock:
        return {
            "mcpo_process_running": (controller.mcpo_process is not None and controller.mcpo_process.returncode is None),
            **app_state
        }