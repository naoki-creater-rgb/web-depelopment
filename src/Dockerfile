# バックエンド（FastAPI）用イメージ
FROM python:3.12-slim

WORKDIR /app

# 依存だけ先にインストール（レイヤーキャッシュを効かせる）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体
COPY . .

EXPOSE 8000

# 本番相当の起動。開発時は docker-compose 側で --reload に上書きする
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
