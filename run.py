#!/usr/bin/env python
# run.py
import os
import typer
import uvicorn
from typing_extensions import Annotated
from dotenv import load_dotenv

# [核心优化] 在所有代码执行前，加载 .env 文件中的环境变量
load_dotenv()

# 创建一个 Typer 应用实例
app = typer.Typer(
    add_completion=False,
    help="🚀 MCPO Watcher 服务启动器：管理 FastAPI 监控应用和 MCPO 子进程。",
    rich_markup_mode="markdown"
)

@app.command()
def main(
    # [核心优化] 使用 Typer 的 'envvar' 参数，使其自动从环境变量读取值
    # 优先级: 命令行参数 > 环境变量 (.env) > 硬编码默认值
    host: Annotated[str, typer.Option(
        "-h", "--host",
        help="监控服务绑定的主机名或 IP 地址。",
        envvar="WATCHER_HOST"  # <-- 对应 .env 中的 WATCHER_HOST
    )] = "0.0.0.0",
    
    port: Annotated[int, typer.Option(
        "-p", "--port",
        help="监控服务监听的端口号。",
        envvar="WATCHER_PORT"  # <-- 对应 .env 中的 WATCHER_PORT
    )] = 8000,

    mcpo_port: Annotated[int, typer.Option(
        "--mcpo-port",
        help="要为 MCPO 子进程分配的端口号。",
        envvar="MCPO_PORT"     # <-- 对应 .env 中的 MCPO_PORT
    )] = 8080,
    
    log_level: Annotated[str, typer.Option(
        "--log-level",
        help="设置日志级别 (例如 'info', 'debug', 'warning')。",
        envvar="LOG_LEVEL"     # <-- 对应 .env 中的 LOG_LEVEL
    )] = "info",

    reload: Annotated[bool, typer.Option(
        "--reload/--no-reload", help="为监控服务启用或禁用热重载模式。"
    )] = False,
):
    """
    启动 MCPO Watcher 服务。

    该服务会启动一个 FastAPI 应用作为监控API，并管理一个 `mcpo` 子进程。
    """
    print("--- 🚀 MCPO Watcher Configuration ---")
    if host == "0.0.0.0":
        print(f"  - 监控服务 API (Local):   http://127.0.0.1:{port}")
        print(f"  - 监控服务 API (Network): http://{host}:{port} (或通过您的局域网IP访问)")
    else:
        print(f"  - 监控服务 API (FastAPI): http://{host}:{port}")
    print(f"  - MCPO 子进程端口: {mcpo_port}")
    print(f"  - 日志级别: {log_level}")
    print(f"  - 监控服务热重载: {'✅' if reload else '❌'}")
    print("------------------------------------")

    # 将 mcpo 的端口号设置到环境变量中，以便 FastAPI 应用内部可以读取
    # 这是必须的，因为 controller.py 是在 uvicorn 启动的子进程中运行的
    os.environ["MCPO_PORT"] = str(mcpo_port)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        workers=1,
    )

if __name__ == "__main__":
    app()