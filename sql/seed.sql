-- =====================================================================
-- 検証環境用 初期データ（seed）
--   schema.sql の後に実行される想定（docker-entrypoint-initdb.d で 02_）
--   ※ password_hash はアプリがそのまま平文比較するため、ログイン確認用に
--     「送るパスワードと同じ文字列」を入れている（検証用。実運用は要ハッシュ化）
-- =====================================================================
USE event_app_db;

-- ---- ユーザー ----
INSERT INTO users (user_id, password_hash, display_name) VALUES
  ('manager_1', 'pass_manager', '幹事タロウ'),
  ('guest_1',   'pass1',        '参加者ハナコ'),
  ('guest_2',   'pass2',        '参加者ジロウ'),
  ('guest_3',   'pass3',        '参加者サブロウ');

-- ---- イベント ----
--   event 1: 計画中（回答受付中）
--   event 2: 確定済み（confirmed_* は候補作成後に UPDATE で設定）
INSERT INTO events
  (event_id, manager_id, event_name, response_deadline, description, status, desired_budget,
   confirmed_shop_name, confirmed_budget, payment_destination, paypay_link)
VALUES
  (1, 'manager_1', '歓迎会2026', '2026-07-20 18:00',
      '新メンバーの歓迎会です。希望の日程・エリアを教えてください！', 'planning', 4000,
      NULL, NULL, NULL, NULL),
  (2, 'manager_1', '送別会2026', '2026-06-30 18:00',
      'お世話になった方の送別会。', 'confirmed', 6000,
      '居酒屋 送別亭', 6000, 'みずほ銀行 ○○支店 普通 1234567', NULL);

-- ---- 候補日時 ----
INSERT INTO event_date_candidates (date_candidate_id, event_id, proposed_datetime, total_score) VALUES
  (1, 1, '2026-08-05 19:00', 9),
  (2, 1, '2026-08-06 19:00', 5),
  (3, 2, '2026-07-10 19:00', 0);

-- ---- 候補エリア ----
INSERT INTO event_area_candidates (area_candidate_id, event_id, proposed_area, total_score) VALUES
  (1, 1, '新宿', 0),
  (2, 1, '渋谷', 0),
  (3, 2, '池袋', 0);

-- ---- 確定イベント(event 2)の確定参照を設定（候補が揃った後）----
UPDATE events
   SET confirmed_datetime_id = 3,
       confirmed_area_id = 3
 WHERE event_id = 2;

-- ---- 参加者（基本回答含む）----
--   guest_1 / guest_3 は回答済み、guest_2 は未回答
INSERT INTO event_participants (event_id, user_id, preferred_budget, preferred_area_id, overall_comment) VALUES
  (1, 'guest_1', 4000, 1,    'よろしくお願いします！'),
  (1, 'guest_2', NULL, NULL, NULL),
  (1, 'guest_3', 5000, 2,    '楽しみにしています');

-- ---- 候補日ごとの回答 ----
INSERT INTO participant_date_responses (event_id, user_id, date_candidate_id, score, comment) VALUES
  (1, 'guest_1', 1, 5, 'この日程がベスト'),
  (1, 'guest_1', 2, 3, '可能ではあります'),
  (1, 'guest_3', 1, 4, 'OKです'),
  (1, 'guest_3', 2, 2, 'できれば避けたい');
