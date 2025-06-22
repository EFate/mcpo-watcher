```
mcpo-watcher/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用主入口，协调所有模块工作
│   ├── models.py            # Pydantic模型，仅定义URL服务和顶层配置结构
│   ├── validator.py         # 服务验证器，只负责Ping URL地址
│   ├── controller.py        # 管理 'mcpo' 主进程的生命周期
│   └── watcher.py           # 监控 config.json 文件变化
├── config.json
├── .env                  # 环境变量配置文件
├── requirements.txt
├── run.py                # 基于Typer的服务启动器
├── Dockerfile            
└── docker-compose.yml    
```

