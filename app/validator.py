import httpx
from typing import Tuple

from .models import Config, UrlBasedServer

async def ping_url(name: str, server: UrlBasedServer) -> Tuple[bool, str]:
    """
    Ping一个基于URL的服务，特别优化了对SSE流式端点的处理。
    它使用流式GET请求来验证连接，而不是HEAD请求。
    """
    print(f"Pinging service '{name}' at {server.url}...")
    try:
        # 使用 httpx.AsyncClient 并设置一个合理的超时
        async with httpx.AsyncClient(timeout=10.0) as client:
            
            # 关键改动：使用 client.stream("GET", ...)
            # 这会发起一个GET请求，但允许我们先处理响应头和状态码，
            # 而不是等待整个响应体（对于SSE流来说是无限的）。
            async with client.stream("GET", server.url, headers=server.headers) as response:
                
                # 检查HTTP状态码。任何非成功状态码都表示失败。
                if not response.is_success:
                    msg = f"FAIL: Service '{name}' at {server.url} returned status {response.status_code}"
                    print(msg)
                    return False, msg

                # （推荐）最佳实践：检查Content-Type是否为 'text/event-stream'
                content_type = response.headers.get("content-type", "").lower()
                if "text/event-stream" not in content_type:
                    msg = (f"WARN: Service '{name}' is reachable, but Content-Type "
                           f"'{content_type}' is not 'text/event-stream'.")
                    print(msg)
                    # 我们将此视为一个警告，但仍然是成功的ping，因为服务是可达的。
                    return True, msg
                
                # 如果状态码成功并且Content-Type正确，则是完美的成功。
                msg = f"OK: Service '{name}' is reachable and configured for SSE (Status: {response.status_code})"
                print(msg)
                return True, msg

    except httpx.RequestError as e:
        # 捕获连接超时、DNS错误等网络层面的问题。
        msg = f"FAIL: Cannot connect to service '{name}' at {server.url}. Error: {e.__class__.__name__}"
        print(msg)
        return False, msg

async def validate_all_services(config: Config) -> Tuple[bool, str]:
    """
    遍历并验证配置文件中的所有服务。
    (此函数无需改动)
    """
    for name, server_config in config.mcp_servers.items():
        is_ok, message = await ping_url(name, server_config)
        if not is_ok:
            # 任何一个服务验证失败，则立即中止并返回
            return False, message
    return True, "All services validated successfully."