# src/test/test_user.py
import datetime
from database import SessionLocal, engine, Base
from sqlalchemy.orm import Session

from repositories.user_repository import UserRepository
from models.event_entity import Event
from models.participant_entity import EventParticipant

# --- ここが重要！全てのモデルを事前に読み込む ---
from models.user_entity import User
from models.event_entity import Event
from models.participant_entity import EventParticipant
from models.date_response_entity import DateResponse
# 以下、まだテストで直接使わなくても、紐付けのためにインポートが必要
# （ファイル名やクラス名が異なる場合は適宜調整してください）
from models.date_candidate_entity import EventDateCandidate 
from models.area_candidate_entity import EventAreaCandidate

def main():
    print("--- UserRepository テスト開始 ---")
    
    # 1. データベースの初期化
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()

    try:
        # --- 2. ユーザー作成テスト (createUser) ---
        print("\n[テスト] createUser 実行中...")
        u1 = UserRepository.createUser(db, "manager_1", "pass_hash_1", "幹事太郎")
        u2 = UserRepository.createUser(db, "guest_1", "pass_hash_2", "参加者A")
        u3 = UserRepository.createUser(db, "guest_2", "pass_hash_3", "参加者B")
        print(f"-> ユーザー作成成功: {u1.display_name}, {u2.display_name}, {u3.display_name}")

        # --- 3. パスワードハッシュ取得テスト (findPasswordHashById) ---
        print("\n[テスト] findPasswordHashById 実行中...")
        p_hash = UserRepository.findPasswordHashById(db, "manager_1")
        print(f"-> 取得したハッシュ: {p_hash} (期待値: pass_hash_1)")

        # --- 4. ユーザーIDによる検索テスト (findUserById) ---
        print("\n[テスト] findUserById 実行中...")
        found_user = UserRepository.findUserById(db, "guest_1")
        print(f"-> 検索結果: {found_user.display_name if found_user else 'None'} (期待値: 参加者A)")

        # --- 5. 名前による検索テスト (findIdByName) ---
        print("\n[テスト] findIdByName 実行中...")
        named_users = UserRepository.findIdByName(db, "参加者B")
        print(f"-> 該当件数: {len(named_users)} (期待値: 1)")

        # --- 6. 過去の参加者取得テスト (findPastRecipients) ---
        print("\n[テスト] findPastRecipients 実行中...")
        
        # テスト用データの準備: 
        # manager_1 が幹事のイベントを作成し、guest_1 と guest_2 を参加させる
        new_event = Event(
            event_id=1,
            manager_id="manager_1",
            event_name="過去のイベント",
            response_deadline=datetime.datetime.now(),
            status="confirmed"
        )
        db.add(new_event)
        db.flush() # IDを確定させる

        p1 = EventParticipant(event_id=1, user_id="guest_1")
        p2 = EventParticipant(event_id=1, user_id="guest_2")
        db.add_all([p1, p2])
        db.commit()

        # 実行
        past_users = UserRepository.findPastRecipients(db, "manager_1")
        print(f"-> 過去の参加者数: {len(past_users)} (期待値: 2)")
        for u in past_users:
            print(f"   - 参加者名: {u.display_name}")

        print("\n--- 全てのユーザー・テストが正常に終了しました ---")

    except Exception as e:
        db.rollback()
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()