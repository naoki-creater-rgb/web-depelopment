from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

# 環境変数から DATABASE_URL を読み込み
_db_url = os.getenv(
    "DATABASE_URL",
    "mysql://root:Dendai.7091@127.0.0.1/event_app_db?charset=utf8mb4"
)
# PyMySQLドライバに変更（localhost の代わりに 127.0.0.1 を使用）
SQLALCHEMY_DATABASE_URL = _db_url.replace("mysql://", "mysql+pymysql://", 1) if "mysql://" in _db_url else _db_url

# エンジンの作成
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # 接続の有効性チェック
    echo=True  # SQL実行ログ出力（デバッグ用）
)

# セッションファクトリの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baseクラスの作成（各Entityモデルはこのクラスを継承して作成します）
Base = declarative_base()

# DBセッションを取得するための依存性注入用関数 (FastAPIなどでよく使われます)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Repository層用：コンテキストマネージャーでセッション自動管理
@contextmanager
def get_session():
    """セッションを自動管理するコンテキストマネージャー"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()