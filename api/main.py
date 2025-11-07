"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import channels, llm, articles, config, workflows

app = FastAPI(
    title="AI内容创作与分发平台 API",
    description="提供内容创作、频道管理、工作流等功能的 RESTful API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(channels.router, prefix="/api/v1", tags=["channels"])
app.include_router(llm.router, prefix="/api/v1", tags=["llm"])
app.include_router(articles.router, prefix="/api/v1", tags=["articles"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(workflows.router, prefix="/api/v1", tags=["workflows"])


@app.get("/")
async def root():
    """根路径"""
    return {"message": "AI内容创作与分发平台 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}

