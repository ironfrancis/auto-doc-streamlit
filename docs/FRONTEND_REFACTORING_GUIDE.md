# Streamlit 前端重构指南

本文档说明如何将现有的 Streamlit 前端重构为调用 FastAPI 后端接口。

## 概述

新的架构将业务逻辑从 Streamlit 页面分离到 FastAPI 后端，Streamlit 只负责 UI 展示和用户交互。

## API 客户端

创建一个统一的 API 客户端：

```python
# core/utils/api_client.py
import httpx
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
    
    async def get_channels(self):
        """获取所有频道"""
        response = await self.client.get("/api/v1/channels")
        response.raise_for_status()
        return response.json()
    
    async def create_channel(self, channel_data: dict):
        """创建频道"""
        response = await self.client.post("/api/v1/channels", json=channel_data)
        response.raise_for_status()
        return response.json()
    
    async def start_workflow(self, workflow_type: str, workflow_data: dict):
        """启动工作流"""
        endpoint = f"/api/v1/workflows/{workflow_type}"
        response = await self.client.post(endpoint, json=workflow_data)
        response.raise_for_status()
        return response.json()
    
    async def get_workflow_status(self, workflow_id: str):
        """获取工作流状态"""
        response = await self.client.get(f"/api/v1/workflows/{workflow_id}")
        response.raise_for_status()
        return response.json()
```

## 重构示例

### 频道管理页面

**之前（直接操作 JSON）：**
```python
from core.channel.channel_management import ChannelManager

manager = ChannelManager()
channels = manager.get_all_channels()
```

**之后（调用 API）：**
```python
from core.utils.api_client import APIClient
import asyncio

client = APIClient()

# 在 Streamlit 中使用
if st.button("加载频道"):
    channels = asyncio.run(client.get_channels())
    st.write(channels)
```

### 内容创作页面

**之前（直接调用 LLM）：**
```python
from pages.1_Creation_and_AI_Transcription import call_single_llm_endpoint

result = call_single_llm_endpoint(endpoint_config, prompt)
```

**之后（使用工作流）：**
```python
from core.utils.api_client import APIClient
import asyncio

client = APIClient()

# 启动内容创作工作流
workflow_data = {
    "input_content": user_input,
    "channel_id": selected_channel,
    "llm_endpoint": endpoint_id
}

result = asyncio.run(
    client.start_workflow("content-creation", workflow_data)
)

workflow_id = result["workflow_id"]

# 轮询工作流状态
while True:
    status = asyncio.run(client.get_workflow_status(workflow_id))
    if status["status"] == "completed":
        break
    time.sleep(1)
```

## 迁移步骤

1. **创建 API 客户端**：在 `core/utils/api_client.py` 中创建统一的 API 客户端
2. **逐步重构页面**：从简单的页面开始，逐步重构
3. **保持向后兼容**：在重构过程中，可以保留旧的 JSON 操作作为后备
4. **测试**：确保每个重构的页面都能正常工作

## 注意事项

- Streamlit 是同步的，但 FastAPI 是异步的，需要使用 `asyncio.run()` 或 `st.rerun()` 来处理异步调用
- 对于长时间运行的工作流，使用轮询或 WebSocket 来获取状态更新
- 错误处理：确保 API 调用失败时有适当的错误提示

