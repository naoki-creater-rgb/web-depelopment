import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base

# エンティティとリポジトリをインポート
from models.user_entity import User
from models.event_entity import Event
from models.participant_entity import EventParticipant
from models.date_response_entity import DateResponse
from repositories.candidate_repository import EventCandidateRepository

def main():
    # 1. テーブルの自動生成
    # 開発用: 毎回まっさらな状態からテストするために一度テーブルを削除して作り直します
    print("テーブルを初期化しています...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # データベースセッションの取得
    db: Session = SessionLocal()

    try:
        # ==========================================
        # 1. 前提となるダミーデータの挿入
        # ==========================================
        print("\n--- 1. 前提ダミーデータの作成 ---")
        
        # 幹事と参加者の作成
        manager = User(user_id="user_manager", password_hash="hash1", display_name="幹事の山田")
        participant_user = User(user_id="user_guest", password_hash="hash2", display_name="参加者の鈴木")
        db.add_all([manager, participant_user])
        db.commit()

        # イベントの作成
        test_event = Event(
            manager_id="user_manager",
            event_name="プロジェクト打ち上げ",
            response_deadline=datetime.datetime(2026, 4, 30)
        )
        db.add(test_event)
        db.commit()
        db.refresh(test_event) # 自動採番された event_id を取得
        event_id = test_event.event_id
        print(f"イベント作成完了 (Event ID: {event_id})")

        # ==========================================
        # 2. リポジトリの Insert メソッドのテスト
        # ==========================================
        print("\n--- 2. 候補日・エリアの登録テスト ---")
        
        dates_to_insert = [datetime.datetime(2026, 5, 1, 19, 0), datetime.datetime(2026, 5, 2, 19, 0)]
        areas_to_insert = ["新宿", "渋谷", "東京"]

        # 候補日の登録
        inserted_dates = EventCandidateRepository.bulkInsertDateCandidates(db, event_id, dates_to_insert)
        for d in inserted_dates:
            print(f"追加された候補日: ID={d.date_candidate_id}, 日時={d.proposed_datetime}")

        # エリアの登録
        inserted_areas = EventCandidateRepository.bulkInsertAreaCandidates(db, event_id, areas_to_insert)
        for a in inserted_areas:
            print(f"追加されたエリア: ID={a.area_candidate_id}, エリア={a.proposed_area}")

        # ==========================================
        # 3. 集計テスト用の「回答データ」を挿入
        # ==========================================
        print("\n--- 3. 参加者による回答データの作成 ---")
        
        # 鈴木さんを参加者として登録。希望エリアは「新宿」（inserted_areasの1つ目）を選択
        shinjuku_id = inserted_areas[0].area_candidate_id
        participant_data = EventParticipant(
            event_id=event_id,
            user_id="user_guest",
            preferred_budget=5000,
            preferred_area_id=shinjuku_id,
            overall_comment="新宿希望です！"
        )
        db.add(participant_data)
        db.commit()

        # 鈴木さんの日程回答を作成
        # 注意: 今回 func.sum() で集計するため、scoreには数値として計算できる文字列を入れています
        response_day1 = DateResponse(
            event_id=event_id,
            user_id="user_guest",
            date_candidate_id=inserted_dates[0].date_candidate_id,
            score="3" # 例: 〇=3点
        )
        response_day2 = DateResponse(
            event_id=event_id,
            user_id="user_guest",
            date_candidate_id=inserted_dates[1].date_candidate_id,
            score="1" # 例: △=1点
        )
        db.add_all([response_day1, response_day2])
        db.commit()
        print("回答データの登録完了")

        # ==========================================
        # 4. リポジトリの Update (集計) メソッドのテスト
        # ==========================================
        print("\n--- 4. 集計・スコア更新テスト ---")
        
        updated_dates = EventCandidateRepository.updateDateCandidateScores(db, event_id)
        for d in updated_dates:
            print(f"集計後の候補日: {d.proposed_datetime} -> 合計スコア: {d.total_score}")

        updated_areas = EventCandidateRepository.updateAreaCandidateScores(db, event_id)
        for a in updated_areas:
            print(f"集計後のエリア: {a.proposed_area} -> 希望者数: {a.total_score}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()