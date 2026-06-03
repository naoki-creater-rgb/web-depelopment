# src/test/test_response.py
import datetime
from database import SessionLocal, engine, Base
from sqlalchemy.orm import Session

# --- 1. 全てのモデルをインポート（テーブル作成とリレーションのために必須） ---
from models.user_entity import User
from models.event_entity import Event
from models.participant_entity import EventParticipant
from models.date_response_entity import DateResponse
from models.area_candidate_entity import EventAreaCandidate
from models.date_candidate_entity import EventDateCandidate

from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from repositories.response_repository import EventParticipantRepository

def main():
    print("--- EventParticipantRepository 統合テスト開始 ---")
    
    # データベース初期化
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # --- 2. 基礎データの作成 ---
        print("\n[準備] ユーザーとイベントを作成中...")
        UserRepository.createUser(db, "manager_id", "hash", "幹事さん")
        UserRepository.createUser(db, "user1", "hash", "参加者1")
        UserRepository.createUser(db, "user2", "hash", "参加者2")
        
        deadline = datetime.datetime.now() + datetime.timedelta(days=7)
        event = EventRepository.createEvent(db, "manager_id", "集計テスト飲み会", deadline, "詳細")
        eid = event.event_id

        # エリア候補の作成 (EventParticipant.preferred_area_id の参照先)
        area = EventAreaCandidate(event_id=eid, proposed_area="新宿")
        db.add(area)
        
        # 日程候補の作成 (DateResponse.date_candidate_id の参照先)
        date_cand = EventDateCandidate(event_id=eid, proposed_datetime=datetime.datetime(2026, 5, 1, 19, 0))
        db.add(date_cand)
        
        db.commit()
        db.refresh(area)
        db.refresh(date_cand)

        # 変数 aid と did の定義
        aid = area.area_candidate_id
        did = date_cand.date_candidate_id

        # --- 3. 参加者登録 ---
        print("\n[テスト] 参加者を一括登録中...")
        EventParticipantRepository.bulkInsertParticipants(db, eid, ["user1", "user2"])

        # --- 4. 基本回答とエリア集計のテスト ---
        print("\n[テスト] updateParticipantBaseResponse (エリア集計) 実行中...")
        # 2人が新宿(aid)を選択
        EventParticipantRepository.updateParticipantBaseResponse(db, eid, "user1", 5000, aid, "新宿希望")
        EventParticipantRepository.updateParticipantBaseResponse(db, eid, "user2", 6000, aid, "どこでも")
        
        # エリアの total_score が 2 になっているか確認
        db.refresh(area)
        print(f"-> 新宿の選択数: {area.total_score} (期待値: 2)")

        # --- 5. 日程回答とスコア集計のテスト (UPSERT) ---
        print("\n[テスト] upsertDateResponse (日程集計) 実行中...")
        # user1: 2点, user2: 1点 を入力
        EventParticipantRepository.upsertDateResponse(db, eid, "user1", did, 2, "いける")
        EventParticipantRepository.upsertDateResponse(db, eid, "user2", did, 1, "たぶんいける")
        
        # 日程の total_score が 2+1=3 になっているか確認
        db.refresh(date_cand)
        print(f"-> 候補日の合計スコア: {date_cand.total_score} (期待値: 3)")

        # --- 6. スコア更新時の再集計テスト ---
        print("\n[テスト] スコア更新時の再集計 実行中...")
        # user2 がスコアを 1点 -> 0点 に変更
        EventParticipantRepository.upsertDateResponse(db, eid, "user2", did, 0, "やっぱり無理")
        
        # 日程の total_score が 2+0=2 になっているか確認
        db.refresh(date_cand)
        print(f"-> 更新後の合計スコア: {date_cand.total_score} (期待値: 2)")

        print("\n--- 全てのレスポンス・集計テストが正常に終了しました ---")

    except Exception as e:
        db.rollback()
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()