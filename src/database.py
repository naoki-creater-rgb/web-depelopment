from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# ユーザー名、パスワード、ホスト名、DB名を環境に合わせて変更してください
# 例: rootユーザー、パスワード"password"、ローカルホストの場合
SQLALCHEMY_DATABASE_URL = "mysql://root:Dendai.7091@localhost/event_app_db?charset=utf8mb4"

# エンジンの作成
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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