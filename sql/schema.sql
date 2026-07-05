-- =====================================================================
-- イベント調整アプリ  データベーススキーマ（検証環境用）
-- 対象: MySQL 8.x / InnoDB / utf8mb4
-- 生成元: src/models/*.py および draw_io/DB_ER_diagram.drawio
--
-- 使い方（例）:
--   mysql -u root -p < sql/schema.sql
-- もしくは MySQL クライアントに接続して本ファイルを流し込む。
-- 何度でも流し直せるよう、既存テーブルを DROP してから再作成する。
-- =====================================================================

CREATE DATABASE IF NOT EXISTS event_app_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE event_app_db;

-- 依存関係を無視して一旦全削除（再実行しやすくするため）
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS participant_date_responses;
DROP TABLE IF EXISTS event_participants;
DROP TABLE IF EXISTS event_area_candidates;
DROP TABLE IF EXISTS event_date_candidates;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;


-- ---------------------------------------------------------------------
-- users : ユーザー
-- ---------------------------------------------------------------------
CREATE TABLE users (
  user_id       VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  display_name  VARCHAR(255) NOT NULL,
  PRIMARY KEY (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- events : イベント本体
--   confirmed_* 系は status が confirmed / completed のときに埋まる。
--   confirmed_datetime_id への FK は event_date_candidates 作成後に
--   ALTER TABLE で後付けする（相互参照のため）。
-- ---------------------------------------------------------------------
CREATE TABLE events (
  event_id              INT          NOT NULL AUTO_INCREMENT,
  manager_id            VARCHAR(255) NOT NULL,
  event_name            VARCHAR(255) NOT NULL,
  response_deadline     DATETIME     NOT NULL,
  description           TEXT,
  status                ENUM('planning','confirmed','completed')
                                     NOT NULL DEFAULT 'planning',
  desired_budget        INT,

  -- 確定情報（任意 / 確定時に設定）
  confirmed_area_id     INT,
  confirmed_shop_name   VARCHAR(255),
  confirmed_budget      INT,
  confirmed_datetime_id INT,
  payment_destination   VARCHAR(255),
  paypay_link           VARCHAR(255),

  PRIMARY KEY (event_id),
  KEY idx_events_manager_id (manager_id),
  CONSTRAINT fk_events_manager
    FOREIGN KEY (manager_id) REFERENCES users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- event_date_candidates : 候補日時
-- ---------------------------------------------------------------------
CREATE TABLE event_date_candidates (
  date_candidate_id INT      NOT NULL AUTO_INCREMENT,
  event_id          INT      NOT NULL,
  proposed_datetime DATETIME NOT NULL,
  total_score       INT      DEFAULT 0,
  PRIMARY KEY (date_candidate_id),
  KEY idx_date_candidates_event_id (event_id),
  CONSTRAINT fk_date_candidates_event
    FOREIGN KEY (event_id) REFERENCES events (event_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- event_area_candidates : 候補エリア
-- ---------------------------------------------------------------------
CREATE TABLE event_area_candidates (
  area_candidate_id INT          NOT NULL AUTO_INCREMENT,
  event_id          INT          NOT NULL,
  proposed_area     VARCHAR(255) NOT NULL,
  total_score       INT          DEFAULT 0,
  PRIMARY KEY (area_candidate_id),
  KEY idx_area_candidates_event_id (event_id),
  CONSTRAINT fk_area_candidates_event
    FOREIGN KEY (event_id) REFERENCES events (event_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- event_participants : イベント参加者（基本回答を含む）
--   複合主キー (event_id, user_id)
-- ---------------------------------------------------------------------
CREATE TABLE event_participants (
  event_id          INT          NOT NULL,
  user_id           VARCHAR(255) NOT NULL,
  preferred_budget  INT,
  preferred_area_id INT,
  overall_comment   TEXT,
  PRIMARY KEY (event_id, user_id),
  KEY idx_participants_user_id (user_id),
  KEY idx_participants_pref_area (preferred_area_id),
  CONSTRAINT fk_participants_event
    FOREIGN KEY (event_id) REFERENCES events (event_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_participants_user
    FOREIGN KEY (user_id) REFERENCES users (user_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_participants_pref_area
    FOREIGN KEY (preferred_area_id) REFERENCES event_area_candidates (area_candidate_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- participant_date_responses : 候補日ごとの参加者回答
--   複合主キー (event_id, user_id, date_candidate_id)
--   (event_id, user_id) は event_participants への複合 FK
-- ---------------------------------------------------------------------
CREATE TABLE participant_date_responses (
  event_id          INT          NOT NULL,
  user_id           VARCHAR(255) NOT NULL,
  date_candidate_id INT          NOT NULL,
  score             INT          NOT NULL,
  comment           TEXT,
  PRIMARY KEY (event_id, user_id, date_candidate_id),
  KEY idx_responses_date_candidate (date_candidate_id),
  CONSTRAINT fk_responses_participant
    FOREIGN KEY (event_id, user_id)
    REFERENCES event_participants (event_id, user_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_responses_date_candidate
    FOREIGN KEY (date_candidate_id)
    REFERENCES event_date_candidates (date_candidate_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 相互参照の FK を後付け
--   events.confirmed_datetime_id -> event_date_candidates.date_candidate_id
--   events.confirmed_area_id     -> event_area_candidates.area_candidate_id
--     ※ confirmed_area_id は ER 図で FK 指定のため追加。
--     ※ 削除時は両方とも SET NULL。参照先の候補が消えても「イベント自体は
--       残す」ため（候補日削除でイベントごと消えるのを防ぐ）。
--       src/models/event_entity.py の定義とも一致。
-- ---------------------------------------------------------------------
ALTER TABLE events
  ADD CONSTRAINT fk_events_confirmed_datetime
    FOREIGN KEY (confirmed_datetime_id)
    REFERENCES event_date_candidates (date_candidate_id)
    ON DELETE SET NULL,
  ADD CONSTRAINT fk_events_confirmed_area
    FOREIGN KEY (confirmed_area_id)
    REFERENCES event_area_candidates (area_candidate_id)
    ON DELETE SET NULL;
