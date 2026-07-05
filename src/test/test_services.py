# src/test/test_services.py
import sys
import os
import datetime
from pathlib import Path

# パス設定
sys.path.insert(0, str(Path(__file__).parent.parent))

# テスト用のSQLiteエンジン設定
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# テスト用DB（SQLite）
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DB_URL, echo=False)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base = declarative_base()
from models.user_entity import User
from models.event_entity import Event, Status
from models.participant_entity import EventParticipant
from models.date_candidate_entity import EventDateCandidate
from models.area_candidate_entity import EventAreaCandidate
from models.date_response_entity import DateResponse
from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from repositories.candidate_repository import EventCandidateRepository
from repositories.response_repository import EventParticipantRepository
from services.participant_service import ParticipantService
from services.organizer_service import OrganizerService

# テスト用モデルをBase に登録
Base.metadata.bind = test_engine

# すべてのテーブルをSQLiteに作成
def create_all_tables():
    """すべてのモデルテーブルをSQLiteに作成"""
    # モデルクラスをすべてインポートしてBASEに登録
    Base.metadata.create_all(bind=test_engine)

def main():
    print("=" * 60)
    print("Services Layer テスト開始")
    print("=" * 60)

    # 1. データベース初期化（テスト用SQLite）
    print("\n[準備] テスト用データベース初期化中...")
    Base.metadata.drop_all(bind=test_engine)
    create_all_tables()  # すべてのテーブルを作成
    db: Session = TestSessionLocal()

    try:
        # ===== テストデータ準備 =====
        print("\n[準備] テストデータ作成中...")

        # ユーザー作成
        u_manager = User(user_id="manager_1", password_hash="hash1", display_name="幹事太郎")
        u_guest_1 = User(user_id="guest_1", password_hash="hash2", display_name="参加者A")
        u_guest_2 = User(user_id="guest_2", password_hash="hash3", display_name="参加者B")
        u_guest_3 = User(user_id="guest_3", password_hash="hash4", display_name="参加者C")
        db.add_all([u_manager, u_guest_1, u_guest_2, u_guest_3])
        db.commit()
        print("✓ ユーザー4人作成完了")

        # ===== OrganizerService テスト =====
        print("\n" + "=" * 60)
        print("OrganizerService テスト")
        print("=" * 60)

        # createNewEvent テスト
        print("\n[テスト1] createNewEvent")
        response_deadline = datetime.datetime.now() + datetime.timedelta(days=7)
        candidate_dates = [
            datetime.datetime(2026, 8, 1, 19, 0),
            datetime.datetime(2026, 8, 2, 18, 30)
        ]
        candidate_areas = ["新宿", "渋谷", "池袋"]

        result = OrganizerService.createNewEvent(
            db,
            "manager_1",
            "新年会2026",
            response_deadline.strftime("%Y-%m-%d %H:%M"),
            "今年の新年会です。希望の日程とエリアを教えてください！",
            candidate_areas,
            candidate_dates
        )

        if result["status"] == "success":
            event_id = result["data"]["eventId"]
            print(f"✓ イベント作成成功: ID={event_id}")
            print(f"  - イベント名: {result['data']['eventName']}")
            print(f"  - 候補日数: {len(result['data']['candidateDates'])}")
            print(f"  - 候補エリア数: {len(result['data']['candidateAreas'])}")
        else:
            print(f"✗ イベント作成失敗: {result['message']}")
            return

        # inviteUsers テスト
        print("\n[テスト2] inviteUsers")
        user_ids = ["guest_1", "guest_2", "guest_3"]
        OrganizerService.inviteUsers(db, event_id, user_ids)
        print(f"✓ ユーザー招待完了: {user_ids}")

        # ===== ParticipantService テスト =====
        print("\n" + "=" * 60)
        print("ParticipantService テスト")
        print("=" * 60)

        # getParticipatingEvents テスト
        print("\n[テスト3] getParticipatingEvents")
        result = ParticipantService.getParticipatingEvents(db, "guest_1")
        if result["status"] == "success":
            print(f"✓ 参加イベント取得成功")
            print(f"  - 未回答イベント: {len(result['data']['unanswered'])}")
            print(f"  - 回答済みイベント: {len(result['data']['answered'])}")
            if result['data']['unanswered']:
                print(f"  - 未回答イベント詳細: {result['data']['unanswered'][0]}")
        else:
            print(f"✗ 参加イベント取得失敗: {result['message']}")

        # submitResponse テスト
        print("\n[テスト4] submitResponse")

        # 候補日IDを取得（テストデータから）
        db_event = db.query(Event).filter(Event.event_id == event_id).first()
        date_candidates = db.query(EventDateCandidate).filter(
            EventDateCandidate.event_id == event_id
        ).all()
        area_candidates = db.query(EventAreaCandidate).filter(
            EventAreaCandidate.event_id == event_id
        ).all()

        if not date_candidates or not area_candidates:
            print("✗ テストデータの候補日/エリアが見つかりません")
            return

        # 回答データ作成
        date_responses = [
            ParticipantService.DateResponseInput(
                candidate_id=str(date_candidates[0].date_candidate_id),
                score=5,
                comment="この日程でOK"
            ),
            ParticipantService.DateResponseInput(
                candidate_id=str(date_candidates[1].date_candidate_id),
                score=3,
                comment="調整可能"
            )
        ]

        result = ParticipantService.submitResponse(
            db,
            event_id,
            "guest_1",
            5000,
            area_candidates[0].area_candidate_id,
            "楽しみにしています！",
            date_responses
        )

        if result["status"] == "success":
            print(f"✓ 回答送信成功: {result['message']}")
        else:
            print(f"✗ 回答送信失敗: {result['message']}")

        # ===== OrganizerService 続き =====
        print("\n[テスト5] getManagedEvents")
        result = OrganizerService.getManagedEvents(db, "manager_1")
        if result["status"] == "success":
            print(f"✓ 管理イベント取得成功")
            print(f"  - 計画中: {len(result['data']['planning'])} 件")
            print(f"  - 確定済み: {len(result['data']['confirmed'])} 件")
            print(f"  - 完了: {len(result['data']['completed'])} 件")
        else:
            print(f"✗ 管理イベント取得失敗: {result['message']}")

        # confirmEvent テスト
        print("\n[テスト6] confirmEvent")
        payment_dest = "三菱UFJ銀行 〇〇支店 普通 1234567 マスダ タロウ"
        paypay_link = "https://paypay.me/xxxx/5500"

        result = OrganizerService.confirmEvent(
            db,
            event_id,
            area_candidates[0].area_candidate_id,
            "和食処 ますだ",
            5500,
            date_candidates[0].date_candidate_id,
            payment_dest,
            paypay_link
        )

        if result["status"] == "success":
            print(f"✓ イベント確定成功: {result['message']}")
        else:
            print(f"✗ イベント確定失敗: {result['message']}")

        # 確定後のイベント確認
        print("\n[テスト7] 確定後のイベント状態確認")
        result = OrganizerService.getManagedEvents(db, "manager_1")
        if result["status"] == "success":
            print(f"✓ イベント状態更新確認")
            print(f"  - 計画中: {len(result['data']['planning'])} 件")
            print(f"  - 確定済み: {len(result['data']['confirmed'])} 件")

        print("\n" + "=" * 60)
        print("✅ 全てのサービステストが正常に終了しました")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
