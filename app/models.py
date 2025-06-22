import json
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Optional, Literal

class UrlBasedServer(BaseModel):
    """一个通用的基于URL的MCP服务器模型。"""
    type: Literal["sse", "streamable_http"]
    url: str
    headers: Optional[Dict[str, str]] = None

class Config(BaseModel):
    """顶层配置模型，直接对应 config.json 的结构。"""
    mcp_servers: Dict[str, UrlBasedServer] = Field(..., alias="mcpServers")

    class Config:
        populate_by_name = True

def load_config(path: str = "config.json") -> Optional[Config]:
    """加载并验证 config.json 文件。"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Config.model_validate(data)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at '{path}'")
        return None
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{path}'")
        return None
    except ValidationError as e:
        print(f"Error: Configuration validation failed:\n{e}")
        return None