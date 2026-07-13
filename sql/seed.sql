-- =====================================================================
-- 検証環境用 初期データ（seed）
--   schema.sql の後に実行される想定（docker-entrypoint-initdb.d で 02_）
--   ※ password_hash はアプリがそのまま平文比較するため、ログイン確認用に
--     「送るパスワードと同じ文字列」を入れている（検証用。実運用は要ハッシュ化）
--
--   フロントのテストで一通りの画面/状態を確認できるよう、以下を網羅する:
--     - 幹事が2人（getManagedEvents で人によって結果が変わる）
--     - planning（回答あり / 回答待ち）・confirmed・completed の各ステータス
--     - 回答済み参加者 / 未回答参加者 の両方
--
--   ★データの一覧・ログイン情報は API_Implementation_Guide/seed_data.html を参照
-- =====================================================================
-- 取り込み接続の文字コードを固定（latin1 誤認による日本語の文字化け防止）
SET NAMES utf8mb4;

USE event_app_db;

-- 何度でも流し直せるよう、既存の seed を掃除してから入れ直す
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE participant_date_responses;
TRUNCATE TABLE event_participants;
TRUNCATE TABLE event_area_candidates;
TRUNCATE TABLE event_date_candidates;
TRUNCATE TABLE events;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
-- ユーザー
--   manager_* … 幹事として使うアカウント
--   guest_*   … 参加者として使うアカウント
-- =====================================================================
INSERT INTO users (user_id, password_hash, display_name) VALUES
  ('manager_1', 'pass_manager',  '幹事タロウ'),
  ('manager_2', 'pass_manager2', '幹事ハナコ'),
  ('guest_1',   'pass1',         '参加者ハナコ'),
  ('guest_2',   'pass2',         '参加者ジロウ'),
  ('guest_3',   'pass3',         '参加者サブロウ'),
  ('guest_4',   'pass4',         '参加者シロウ'),
  ('guest_5',   'pass5',         '参加者ゴロウ');

-- =====================================================================
-- イベント
--   event 1: planning（回答あり）        manager_1
--   event 2: confirmed（確定済み）        manager_1
--   event 3: planning（回答待ち／未回答） manager_1
--   event 4: completed（開催済み）        manager_2
--   event 5: planning（回答あり）         manager_2
--   ※ confirmed_* 系は候補作成後に UPDATE で設定する
-- =====================================================================
INSERT INTO events
  (event_id, manager_id, event_name, response_deadline, description, status, desired_budget,
   confirmed_shop_name, confirmed_budget, payment_destination, paypay_link)
VALUES
  (1, 'manager_1', '歓迎会2026', '2026-07-20 18:00',
      '新メンバーの歓迎会です。希望の日程・エリアを教えてください！', 'planning', 4000,
      NULL, NULL, NULL, NULL),
  (2, 'manager_1', '送別会2026', '2026-06-30 18:00',
      'お世話になった方の送別会。', 'confirmed', 6000,
      '居酒屋 送別亭', 6000, 'みずほ銀行 ○○支店 普通 1234567', NULL),
  (3, 'manager_1', '忘年会2026', '2026-12-15 18:00',
      '今年もお疲れさまでした。日程調整にご協力ください。', 'planning', 5000,
      NULL, NULL, NULL, NULL),
  (4, 'manager_2', '新年会2026', '2026-01-05 18:00',
      '新年の顔合わせ。無事に開催しました！', 'completed', 5000,
      '和食処 初春', 5500, 'PayPay送金でお願いします', 'https://paypay.ne.jp/example-shinnenkai'),
  (5, 'manager_2', 'BBQ大会2026', '2026-08-25 18:00',
      '夏の恒例BBQ。エリアと日程の希望をどうぞ。', 'planning', 3500,
      NULL, NULL, NULL, NULL);

-- =====================================================================
-- 候補日時
-- =====================================================================
INSERT INTO event_date_candidates (date_candidate_id, event_id, proposed_datetime, total_score) VALUES
  -- event 1
  (1,  1, '2026-08-05 19:00', 10),
  (2,  1, '2026-08-06 19:00', 3),
  -- event 2（確定日程）
  (3,  2, '2026-07-10 19:00', 0),
  -- event 3（まだ回答なし）
  (4,  3, '2026-12-18 19:00', 0),
  (5,  3, '2026-12-19 19:00', 0),
  (6,  3, '2026-12-20 18:00', 0),
  -- event 4（開催済み。7番が確定日程）
  (7,  4, '2026-01-10 19:00', 13),
  (8,  4, '2026-01-11 19:00', 3),
  -- event 5
  (9,  5, '2026-08-22 17:00', 8),
  (10, 5, '2026-08-23 17:00', 6),
  (11, 5, '2026-08-29 17:00', 0);

-- =====================================================================
-- 候補エリア
-- =====================================================================
INSERT INTO event_area_candidates (area_candidate_id, event_id, proposed_area, total_score) VALUES
  -- event 1
  (1, 1, '新宿',   0),
  (2, 1, '渋谷',   0),
  -- event 2（確定エリア）
  (3, 2, '池袋',   0),
  -- event 3
  (4, 3, '上野',   0),
  (5, 3, '秋葉原', 0),
  -- event 4（確定エリア = 横浜）
  (6, 4, '横浜',   0),
  -- event 5
  (7, 5, '吉祥寺', 0),
  (8, 5, '中野',   0);

-- =====================================================================
-- 確定イベントの確定参照を設定（候補が揃った後に UPDATE）
--   event 2: confirmed / event 4: completed
-- =====================================================================
UPDATE events SET confirmed_datetime_id = 3, confirmed_area_id = 3 WHERE event_id = 2;
UPDATE events SET confirmed_datetime_id = 7, confirmed_area_id = 6 WHERE event_id = 4;

-- =====================================================================
-- 参加者（基本回答含む）
--   preferred_area_id は event_area_candidates.area_candidate_id を指す
-- =====================================================================
INSERT INTO event_participants (event_id, user_id, preferred_budget, preferred_area_id, overall_comment) VALUES
  -- event 1: guest_1 / guest_3 は回答済み、guest_2 は未回答
  (1, 'guest_1', 4000, 1,    'よろしくお願いします！'),
  (1, 'guest_2', NULL, NULL, NULL),
  (1, 'guest_3', 5000, 2,    '楽しみにしています'),
  -- event 3: 参加者はいるが全員まだ未回答（回答待ち状態の確認用）
  (3, 'guest_1', NULL, NULL, NULL),
  (3, 'guest_4', NULL, NULL, NULL),
  -- event 4: 開催済み。全員回答済み
  (4, 'guest_1', 5000, 6, 'ありがとうございました'),
  (4, 'guest_2', 6000, 6, '楽しかったです'),
  (4, 'guest_5', 5000, 6, 'また参加したい'),
  -- event 5: guest_3 / guest_4 が回答済み
  (5, 'guest_3', 3500, 7, '外だと嬉しい'),
  (5, 'guest_4', 3000, 8, 'どこでもOKです');

-- =====================================================================
-- 候補日ごとの回答（participant_date_responses）
-- =====================================================================
INSERT INTO participant_date_responses (event_id, user_id, date_candidate_id, score, comment) VALUES
  -- event 1
  (1, 'guest_1', 1, 5, 'この日程がベスト'),
  (1, 'guest_1', 2, 3, '可能ではあります'),
  (1, 'guest_3', 1, 5, 'OKです'),
  (1, 'guest_3', 2, 0, 'できれば避けたい'),
  -- event 4（開催済み）
  (4, 'guest_1', 7, 5, 'ばっちりです'),
  (4, 'guest_1', 8, 3, NULL),
  (4, 'guest_2', 7, 5, NULL),
  (4, 'guest_2', 8, 0, '少し厳しい'),
  (4, 'guest_5', 7, 3, NULL),
  (4, 'guest_5', 8, 0, NULL),
  -- event 5
  (5, 'guest_3', 9,  5, '一番いい'),
  (5, 'guest_3', 10, 3, NULL),
  (5, 'guest_3', 11, 0, '避けたい'),
  (5, 'guest_4', 9,  3, NULL),
  (5, 'guest_4', 10, 3, NULL),
  (5, 'guest_4', 11, 0, NULL);
