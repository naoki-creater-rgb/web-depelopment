# src/test/test_event_advanced.py
import datetime
from database import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from repositories.event_repository import EventRepository
from repositories.candidate_repository import EventCandidateRepository
from models.user_entity import User
from models.participant_entity import EventParticipant

def main():
    print("--- EventRepository 詳細検証テスト開始 ---")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. ユーザー準備
        u1 = User(user_id="user_a", password_hash="h", display_name="ユーザーA")
        u2 = User(user_id="user_b", password_hash="h", display_name="ユーザーB")
        u3 = User(user_id="user_c", password_hash="h", display_name="ユーザーC")
        db.add_all([u1, u2, u3])
        db.commit()

        # 2. 複数イベント作成テスト
        print("\n[検証1] 複数イベントの作成と幹事別取得")
        # ユーザーAが2つ、ユーザーBが1つイベントを作成
        deadline = datetime.datetime.now() + datetime.timedelta(days=7)
        EventRepository.createEvent(db, "user_a", "Aのイベント1", deadline, "Desc 1")
        EventRepository.createEvent(db, "user_a", "Aのイベント2", deadline, "Desc 2")
        EventRepository.createEvent(db, "user_b", "Bのイベント1", deadline, "Desc 3")

        a_events = EventRepository.findEventsByManagerId(db, "user_a")
        print(f"-> ユーザーAのイベント数: {len(a_events)} (期待値: 2)")
        
        # 3. 複雑な参加関係のテスト
        print("\n[検証2] 複数イベントへの参加紐付け (JOIN検証)")
        # ユーザーCを全てのイベントに参加させる
        all_events = db.query(Base.metadata.tables['events']).all()
        for ev in all_events:
            p = EventParticipant(event_id=ev.event_id, user_id="user_c")
            db.add(p)
        db.commit()

        c_participations = EventRepository.findEventsByParticipantId(db, "user_c")
        print(f"-> ユーザーCの参加イベント数: {len(c_participations)} (期待値: 3)")

        # 4. エッジケース：存在しないイベント
        print("\n[検証3] 存在しないIDでの詳細取得")
        invalid_detail = EventRepository.findEventDetailById(db, 9999)
        print(f"-> ID 9999 の結果: {invalid_detail} (期待値: None)")

        # 5. 詳細データの「深い」検証
        print("\n[検証4] 子データの紐付け精度")
        target_event = a_events[0]
        # 候補日を3つ登録
        dates = [
            datetime.datetime(2026, 6, 1, 12, 0),
            datetime.datetime(2026, 6, 2, 12, 0),
            datetime.datetime(2026, 6, 3, 12, 0)
        ]
        EventCandidateRepository.bulkInsertDateCandidates(db, target_event.event_id, dates)

        # 詳細取得
        detail = EventRepository.findEventDetailById(db, target_event.event_id)
        print(f"-> イベント '{detail.event.event_name}' の候補日個数: {len(detail.dateCandidates)} (期待値: 3)")
        
        # 候補日が他のイベントと混ざっていないかチェック
        other_event = a_events[1]
        other_detail = EventRepository.findEventDetailById(db, other_event.event_id)
        print(f"-> 別イベント '{other_detail.event.event_name}' の候補日個数: {len(other_detail.dateCandidates)} (期待値: 0)")

        print("\n--- 詳細検証が正常に終了しました ---")

    except Exception as e:
        db.rollback()
        print(f"\n❌ エラー: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()