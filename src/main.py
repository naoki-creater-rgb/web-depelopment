"""
アプリケーションのエントリポイント。
各コントローラー（APIRouter）を1つのFastAPIアプリに統合する。

起動方法（src ディレクトリで実行）:
    uvicorn main:app --reload

ブラウザで自動生成ドキュメント:
    http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers.user_auth_controller import router as auth_router
from controllers.manager_controller import router as manager_router
from controllers.participant_controller import router as participant_router
from controllers.event_detail_controller import router as event_detail_router

app = FastAPI(title="イベント調整API")

# CORS設定：Reactなどフロントの開発サーバーからのアクセスを許可
# 本番では allow_origins を実際のフロントのドメインに絞ること
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Create React App
        "http://localhost:5173",   # Vite
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 各コントローラーのルーターを統合
app.include_router(auth_router)
app.include_router(manager_router)
app.include_router(participant_router)
app.include_router(event_detail_router)


@app.get("/")
def health_check():
    """疎通確認用"""
    return {"status": "ok"}
