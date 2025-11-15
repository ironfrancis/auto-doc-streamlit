from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import web2md

app = FastAPI(
    title="Auto-doc-streamlit API",
    description="网页转Markdown等功能的API接口",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(web2md.router)


@app.get("/")
async def root():
    return {
        "message": "Auto-doc-streamlit API",
        "version": "1.0.0",
        "endpoints": {
            "web2md": "/api/web2md/fetch"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}