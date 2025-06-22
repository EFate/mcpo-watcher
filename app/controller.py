import asyncio
import os 
import sys

# 这个变量将持有 mcpo 子进程的引用
mcpo_process: asyncio.subprocess.Process | None = None

# 定义启动mcpo的命令
MCPO_COMMAND = "mcpo"
CONFIG_FILE = "config.json"

async def start_mcpo():
    """启动 MCPO 主进程，并从环境变量中读取端口号。"""
    global mcpo_process
    if mcpo_process and mcpo_process.returncode is None:
        print("MCPO process is already running.")
        return

    # [更新] 从环境变量 'MCPO_PORT' 读取端口号，如果未设置则使用默认值 '8080'
    mcpo_port = os.getenv("MCPO_PORT", "8080")
    
    print(f"Attempting to start MCPO process on port {mcpo_port} with config '{CONFIG_FILE}'...")
    try:
        mcpo_process = await asyncio.create_subprocess_exec(
            MCPO_COMMAND,
            "--port", mcpo_port,       # [新增] 将端口号作为参数传递
            "--config", CONFIG_FILE,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        print(f"MCPO process started successfully with PID: {mcpo_process.pid} on port {mcpo_port}")
    except FileNotFoundError:
        print(f"FATAL: Command '{MCPO_COMMAND}' not found. Please ensure 'mcpo' is installed and accessible in your system's PATH.")
        mcpo_process = None
    except Exception as e:
        print(f"An unexpected error occurred while starting MCPO: {e}")
        mcpo_process = None

async def stop_mcpo():
    """停止当前运行的 MCPO 进程。"""
    global mcpo_process
    if not mcpo_process or mcpo_process.returncode is not None:
        print("MCPO process is not running or already stopped.")
        return

    print(f"Stopping MCPO process with PID: {mcpo_process.pid}...")
    try:
        mcpo_process.terminate()
        await asyncio.wait_for(mcpo_process.wait(), timeout=5.0)
        print("MCPO process stopped.")
    except ProcessLookupError:
        print("MCPO process was already terminated.")
    except asyncio.TimeoutError:
        print("Timeout reached while waiting for MCPO to terminate. Forcing kill.")
        mcpo_process.kill()
    finally:
        mcpo_process = None

async def restart_mcpo():
    """优雅地重启 MCPO 进程。"""
    print("Restarting MCPO process...")
    await stop_mcpo()
    await asyncio.sleep(1)
    await start_mcpo()