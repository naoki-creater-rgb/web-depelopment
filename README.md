# Event Management Web Application (Backend)

イベントの企画から日程・エリアの調整、回答集計、そしてPayPayリンクなどを用いた決済情報の確定までを一気通貫で管理できるイベント調整用Webアプリケーションのバックエンドリポジトリです。

現在、**データベース設計（テーブル定義・案）およびデータモデル/操作関数の設計・実装**フェーズが完了しています。

---

## 1. システム概要と主要機能一覧

システムは主に以下の3つの機能群から構成されます。

### 認証・ユーザー管理機能

* **ユーザー登録**: ユーザーIDと名前、ハッシュ化されたパスワードをデータベースに保存。
* **ログイン・認証**: パスワードの照合を行い、JWT認証トークンを発行。
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

## 2. データベース設計 (Schema)

現在、以下の6つのテーブルが定義されています。

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

#### 4. `event_area_candidates` (幹子が提示したエリア候補)

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

## 3. 実装済みリポジトリ層・DB操作関数

データアクセス層（リポジトリパターンを想定）の設計として、以下の関数が定義されています。

### 認証・ユーザー管理系

* `createUser(id, password, name)`: `users` テーブルへ新規 INSERT。パスワードはハッシュ化して保存。
* `findPasswordHashById(id)`: `users` から指定IDのハッシュ化パスワードを取得しログイン照会に利用。
* `findUserById(id)`: 指定IDの `User` クラスインスタンス（パスワード除く情報）を取得。
* `findPastRecipients(id)`: `events` と `event_participants`、`users` を結合し、自身が過去に招待したことのあるユーザー一覧を一括取得。

### 幹事・イベント管理系

* `createEvent(...)`: ステータスを `'planning'`（検討中）としてイベントの基本レコードを INSERT。
* `bulkInsertDateCandidates(candidates)`: 幹事が提示した複数の候補日時をループまたはバルクで `event_date_candidates` に一括挿入。
* `bulkInsertAreaCandidates(candidates)`: 複数の候補エリアを `event_area_candidates` に一括挿入。
* `findEventsByManagerId(manager_id)`: 自身が作成したイベントを一覧取得（検討中・確定済・開催済に分類して返却）。
* `bulkInsertParticipants(participants)`: 選択した複数のユーザーを `event_participants` に登録（初期状態の希望条件は NULL）。
* `updateDateCandidateScores(event_id)`: 参加者の回答（`participant_date_responses`）を `SUM` 演算し、`event_date_candidates.total_score` をまとめて `UPDATE`。

### 参加者・回答管理系

* `findEventsByParticipating(user_id, filter)`: 招待されているイベントを、回答状況（希望予算等が NULL か否か、または日付回答の有無）に応じて絞り込んで取得。
* `updateParticipantBaseResponse(...)`: `event_participants` の希望予算、希望エリア、全体コメントを `UPDATE`。
* `upsertDateResponses(...)`: 各候補日時に対するスコアと個別コメントについて、既にレコードがあれば `UPDATE`、なければ `INSERT`（UPSERT 処理）。
* `getConfirmedDetails(event_id)`: `events` テーブルを `SELECT` し、ステータスが確定済（`confirmed` / `completed`）の場合に限り、決定した店舗・予算・日時・PayPay等のリンク情報を返却。

---

## 4. 今後の開発ロードマップ

1. **Repositoryクラス・ORMの実装**: SQLアーキテクチャのオブジェクトマッピング（SQLAlchemy等のORMや、プログラミング言語に合わせたリポジトリクラスの具体化）。
2. **ビジネスロジック・サービス層の構築**: 回答集計時の統計（平均・最小・最大予算、エリアの得票カウントなど）を構築するロジックサービス、JWTトークン生成ロジックの実装。
3. **API コントローラー層 (エンドポイント) の実装**: フロントエンドからのJSONリクエスト/レスポンス（設計資料に記載のある `status: "success"` などの規定フォーマット）のルーティング実装。
4. **外部連携テスト**: PayPayリンクのハンドリングおよびフロントエンドのカレンダーコンポーネントとの結合テスト。
