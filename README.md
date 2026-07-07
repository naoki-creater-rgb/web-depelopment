# Event Management Web Application (Backend)

イベントの企画から日程・エリアの調整、回答集計、そしてPayPayリンクなどを用いた決済情報の確定までを一気通貫で管理できるイベント調整用Webアプリケーションのバックエンドリポジトリです。

詳しい設計資料は `設計資料.pdf`、APIの入出力仕様は `リクエストレスポンス一覧.pdf` および `API_Implementation_Guide/` に記載しているため、合わせてご参照ください。

現在、**バックエンドの基本機能（API・サービス・リポジトリ層）の実装が完了**し、Docker Compose で API・MySQL・動作確認用フロントを一括起動できる状態です。

---

## 1. 技術スタック

| レイヤー | 使用技術 |
| --- | --- |
| 言語 | Python 3.12 |
| Webフレームワーク | FastAPI 0.136 / Uvicorn |
| DBアクセス | SQLAlchemy 2.0 + PyMySQL |
| データベース | MySQL 8.0 |
| 認証 | パスワードハッシュ照合 + JWT想定 |
| 実行環境 | Docker / Docker Compose |
| 動作確認用フロント | 静的HTML（nginx配信） |

---

## 2. アーキテクチャ

リクエストは以下の層を通って処理されます。

```
Client (frontend)
   │  HTTP / JSON
   ▼
Controller 層  … FastAPI の APIRouter。ルーティングとリクエストモデル(Pydantic)の受け取り
   ▼
Service 層     … 業務ロジック（集計計算・認証・UPSERT制御など）
   ▼
Repository 層  … SQL の発行・DB操作（テーブルごとに分割）
   ▼
MySQL
```

- **Unit of Work / セッション管理**: `unit_of_work.py`・`database.py` でDBセッションとトランザクションを一元管理。
- **Entity / DTO**: `models/` に各テーブルのエンティティ、`dtos/`・`controllers/models/` にリクエスト/レスポンス用モデルを定義。

### ディレクトリ構成

```
.
├── docker-compose.yml       # API + MySQL + フロントの一括起動定義
├── sql/
│   ├── schema.sql           # テーブル定義（初回起動時に自動実行）
│   └── seed.sql             # 初期データ
├── frontend/
│   └── index.html           # 動作確認用の静的ページ
├── src/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py              # FastAPI エントリポイント（ルーター統合・CORS設定）
│   ├── database.py          # DB接続・エンジン設定
│   ├── unit_of_work.py      # セッション/トランザクション管理
│   ├── controllers/         # APIエンドポイント（auth / organizer / participant）
│   │   └── models/          # リクエスト用 Pydantic モデル
│   ├── services/            # 業務ロジック層
│   ├── repositories/        # DB操作層
│   ├── models/              # テーブルエンティティ
│   ├── dtos/                # データ転送オブジェクト
│   └── test/                # ユニット/結合テスト
└── API_Implementation_Guide/ # API仕様のHTMLリファレンス
```

---

## 3. セットアップと起動

### Docker Compose（推奨）

```bash
# 初回・ビルドから起動
docker compose up --build

# 停止
docker compose down

# DBを初期化してやり直す
docker compose down -v && docker compose up --build
```

| サービス | URL |
| --- | --- |
| 動作確認用フロント | http://localhost:3000 |
| API | http://localhost:8000 |
| API ドキュメント (Swagger UI) | http://localhost:8000/docs |
| MySQL | localhost:3307 （ホストの3306回避のため3307で公開） |

初回起動時、`sql/schema.sql` → `sql/seed.sql` の順でスキーマと初期データが自動投入されます。

### ローカル単体起動（DBは別途用意）

```bash
cd src
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 4. API エンドポイント一覧

`main.py` で認証・幹事・参加者の3ルーターを統合しています。ReactなどのフロントからのアクセスをCORSで許可しています（`localhost:3000` / `localhost:5173`）。

### 認証 (`auth`)

| Method | Path | 概要 |
| --- | --- | --- |
| POST | `/create/new_account` | ユーザー新規登録（パスワードはハッシュ化して保存） |
| POST | `/login` | ログイン・パスワード照合／認証トークン発行 |

### 幹事向け (`organizer`)

| Method | Path | 概要 |
| --- | --- | --- |
| GET | `/manager/events?manager_id=...` | 自身が管理するイベント一覧を取得 |
| POST | `/create/new_event` | 新規イベントを作成（日時候補・エリア候補・招待含む） |
| POST | `/confirm_information` | 日時・予算・店名・PayPayリンク等の確定情報を保存 |

### 参加者向け (`participant`)

| Method | Path | 概要 |
| --- | --- | --- |
| GET | `/participant/events?participant_id=...` | 招待されているイベント一覧を取得 |
| POST | `/participant/create/answer` | 日時候補へのスコア・希望予算・エリア・コメントを回答（UPSERT） |

| その他 | Path | 概要 |
| --- | --- | --- |
| GET | `/` | 疎通確認（ヘルスチェック） |

> リクエスト/レスポンスの具体的なJSON仕様は `リクエストレスポンス一覧.pdf` および `API_Implementation_Guide/frontend_api_reference.html` を参照してください。

---

## 5. 主要機能

### 認証・ユーザー管理機能

* **ユーザー登録**: ユーザーIDと名前、ハッシュ化されたパスワードをデータベースに保存。
* **ログイン・認証**: パスワードの照合を行い、認証トークンを発行。
* **過去の送信先取得**: 自身が過去に幹事として招待したユーザーの履歴を結合（JOIN）により一覧取得。

### 幹事向け機能（イベント管理）

* **イベント新規作成**: イベント名、回答締め切り、カレンダーから選択した日時候補、エリア候補、予算等の初期条件を保存。
* **招待送信（ユーザー紐付け）**: 特定のユーザーを選択し、イベント参加者としてデータベース上で紐付け。
* **回答集計**: 参加者から集まった日時候補の点数、希望予算、希望エリア、全体コメントをバックエンドで計算・集計。
* **イベント確定**: 最終決定した日時、予算、店名、支払先情報、およびPayPay決済リンクを保存して参加者に通知。

### 参加者向け機能（回答管理）

* **参加イベント一覧表示・フィルタリング**: 自身が招待されているイベントを「未回答」「回答済」で絞り込み。
* **回答送信・更新（UPSERT）**: 幹事が提示した日時候補に対するスコア（5点、3点、0点）や個別メモ、希望エリア、全体コメントを保存（再送信時は上書き更新）。
* **確定情報の取得**: ステータスが確定済・開催済になったイベントの最終決定情報（店名やPayPayリンクなど）を閲覧。

---

## 6. データベース設計 (Schema)

以下の6つのテーブルで構成されます（定義は `sql/schema.sql`）。

```
                    +-------------------+
                    |       users       |
                    +-------------------+
                    | PK | user_id      |
                    +----+--------------+
                           |      |
        +------------------+      +-------------------+
        |                                             |
        v                                             v
+------------------------+                  +------------------------+
|         events         |                  |   event_participants   |
+------------------------+                  +------------------------+
| PK | event_id          |                  | PK,FK | user_id        |
| FK | manager_id        |<-- (1:N) --------| PK,FK | event_id       |
+----+-------------------+                  +-------+----------------+
  |            |                                        ^
  |            +------------------+                     |
  v                               v                     |
+------------------------+      +------------------------+   |
| event_date_candidates  |      | event_area_candidates  |   |
+------------------------+      +------------------------+   |
| PK | date_candidate_id |      | PK | area_candidate_id |   |
| FK | event_id          |      | FK | event_id          |   |
+----+-------------------+      +----+-------------------+   |
  ^                                                          |
  |                                                          |
  +-------------------------------------(1:N)----------------+
                                                             |
                                                             v
                                            +------------------------------+
                                            | participant_date_responses   |
                                            +------------------------------+
                                            | PK    | response_id          |
                                            | FK    | event_id             |
                                            | FK    | user_id              |
                                            | FK    | date_candidate_id    |
                                            +-------+----------------------+

```

### テーブル定義詳細

#### 1. `users` (ユーザーマスター)

| Column Name | Type | Description |
| --- | --- | --- |
| `user_id` **(PK)** | VARCHAR | ユーザーID |
| `password_hash` | VARCHAR | パスワード（ハッシュ値） |
| `display_name` | VARCHAR | 名前（表示名） |

#### 2. `events` (イベント基本・確定情報)

| Column Name | Type | Description |
| --- | --- | --- |
| `event_id` **(PK)** | INT | イベントID |
| `manager_id` **(FK)** | VARCHAR | 管理者ID (`users.user_id` へ参照) |
| `event_name` | VARCHAR | イベント名 |
| `response_deadline` | DATETIME | 回答締め切り日時 |
| `description` | TEXT | コメント・詳細 |
| `status` | ENUM/VARCHAR | ステータス (`'planning'`, `'confirmed'`, `'completed'`) |
| `confirmed_area_id` **(FK)** | VARCHAR | 確定エリア |
| `confirmed_shop_name` | VARCHAR | 確定店名 |
| `confirmed_budget` | INT | 確定予算 |
| `confirmed_datetime` | DATETIME | 確定日時 |
| `payment_destination` | TEXT | 支払先情報（銀行口座など） |
| `paypay_link` | VARCHAR | PayPay支払い用リンク |

#### 3. `event_date_candidates` (幹事が提示した日時候補)

| Column Name | Type | Description |
| --- | --- | --- |
| `date_candidate_id` **(PK)** | INT | 日時候補ID |
| `event_id` **(FK)** | INT | 対象イベントID |
| `proposed_datetime` | DATETIME | 候補日時 |
| `total_score` | INT | 回答の合計点数（集計用） |

#### 4. `event_area_candidates` (幹事が提示したエリア候補)

| Column Name | Type | Description |
| --- | --- | --- |
| `area_candidate_id` **(PK)** | INT | エリア候補ID |
| `event_id` **(FK)** | INT | 対象イベントID |
| `proposed_area` | VARCHAR | 候補エリア |

#### 5. `event_participants` (イベント参加者・全体希望)

| Column Name | Type | Key | Description |
| --- | --- | --- | --- |
| `user_id` | VARCHAR | **PK, FK** | 参加者のユーザーID |
| `event_id` | INT | **PK, FK** | 対象のイベントID |
| `preferred_budget` | INT |  | その人の希望予算 |
| `preferred_area` | VARCHAR |  | その人の希望エリア |
| `overall_comment` | TEXT |  | 幹事への全体メッセージ（例:「楽しみ！」） |

#### 6. `participant_date_responses` (日時候補ごとの個別回答)

| Column Name | Type | Key | Description |
| --- | --- | --- | --- |
| `response_id` | INT | **PK** | 回答レコード固有のID |
| `event_id` | INT | **FK** | 対象のイベントID |
| `user_id` | VARCHAR | **FK** | 回答したユーザーのID |
| `date_candidate_id` | INT | **FK** | 幹事が作成した日時候補のID |
| `score` | INT |  | 都合スコア（例: ◯=5点, △=3点, ✕=0点） |
| `comment` | TEXT |  | その日に関する個別メモ（例:「少し遅れます」） |

---

## 7. テスト

`src/test/` にリポジトリ層・サービス層のテストを配置しています。

```bash
cd src
pytest
```

- `test_user.py` / `test_event.py` / `test_candidate.py` / `test_response.py`: リポジトリ層テスト
- `test_services.py` / `test_services_simple.py` / `test_services_mysql.py`: サービス層テスト
- `test_session_debug.py`: セッション管理の検証

---

## 8. 今後の開発ロードマップ

1. **認証の本実装**: JWTの発行・検証、トークンによるエンドポイント保護（現状は認証トークン発行ロジックの整備段階）。
2. **回答集計ロジックの拡充**: 平均・最小・最大予算、エリア得票カウントなどの統計サービスの強化。
3. **フロントエンド本実装**: 動作確認用の静的ページから、Reactなどによる本格的なUIへの置き換え。
4. **外部連携テスト**: PayPayリンクのハンドリングおよびカレンダーコンポーネントとの結合テスト。
</content>
</invoke>
