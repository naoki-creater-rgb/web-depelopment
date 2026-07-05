# src/test/test_services.py
import sys
import datetime
from pathlib import Path

# パス設定
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# --- テスト用DB（インメモリSQLite / 全セッションで1接続を共有）---
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# モデル・サービスを読み込み（models は database.Base に登録される）
from database import Base
from models.user_entity import User
from models.event_entity import Event, Status
from models.participant_entity import EventParticipant
from models.date_candidate_entity import EventDateCandidate
from models.area_candidate_entity import EventAreaCandidate
from models.date_response_entity import DateResponse
from services.participant_service import ParticipantService
from services.organizer_service import OrganizerService

# 入力モデル（controller と同じものを利用）
from controllers.models.manager_models import CreateNewEvent, ConfirmedInformation
from controllers.models.participant_models import (
    ParticipantCreateAnswer,
    AnswerDateResponse,
)

# get_unit_of_work() が使う SessionLocal をテスト用に差し替え
import unit_of_work
unit_of_work.SessionLocal = TestSessionLocal


def seed_users():
    """テスト用ユーザーを投入"""
    db = TestSessionLocal()
    db.add_all([
        User(user_id="manager_1", password_hash="hash1", display_name="幹事太郎"),
        User(user_id="guest_1", password_hash="hash2", display_name="参加者A"),
        User(user_id="guest_2", password_hash="hash3", display_name="参加者B"),
        User(user_id="guest_3", password_hash="hash4", display_name="参加者C"),
    ])
    db.commit()
    db.close()


def main():
    print("=" * 60)
    print("Services Layer テスト開始（インメモリSQLite）")
    print("=" * 60)

    print("\n[準備] テスト用データベース初期化中...")
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    seed_users()
    print("✓ ユーザー4人作成完了")

    # ===== OrganizerService.create_new_event =====
    print("\n[テスト1] create_new_event")
    response_deadline = datetime.datetime.now() + datetime.timedelta(days=7)
    new_event = CreateNewEvent(
        manager_id="manager_1",
        event_name="新年会2026",
        response_deadline=response_deadline.strftime("%Y-%m-%d %H:%M"),
        description="今年の新年会です。希望の日程とエリアを教えてください！",
        candidate_dates=["2026-08-01 19:00", "2026-08-02 18:30"],
        candidate_areas=["新宿", "渋谷", "池袋"],
        desired_budget=5000,
        participants=["guest_1", "guest_2", "guest_3"],
    )
    result = OrganizerService.create_new_event(new_event)
    if result["status"] != "success":
        print(f"✗ イベント作成失敗: {result['message']}")
        return
    event_id = result["data"]["eventId"]
    print(f"✓ イベント作成成功: ID={event_id}")
    print(f"  - 候補日数: {len(result['data']['candidateDates'])}")
    print(f"  - 候補エリア数: {len(result['data']['candidateAreas'])}")
    print(f"  - 参加者数: {len(result['data']['participants'])}")

    # 候補IDは作成結果から取得（テスト内で生セッションを開くと
    # インメモリSQLite+StaticPoolの可視性を壊すため）
    date_candidate_ids = [d["id"] for d in result["data"]["candidateDates"]]
    area_candidate_ids = [a["area_id"] for a in result["data"]["candidateAreas"]]

    # ===== ParticipantService.get_participating_events =====
    print("\n[テスト2] get_participating_events")
    result = ParticipantService.get_participating_events("guest_1")
    if result["status"] == "success":
        print(f"✓ 取得成功 未回答={len(result['data']['unanswered'])} "
              f"回答済={len(result['data']['answered'])}")
    else:
        print(f"✗ 失敗: {result['message']}")

    # ===== ParticipantService.submit_response =====
    print("\n[テスト3] submit_response")
    answer = ParticipantCreateAnswer(
        event_id=event_id,
        user_id="guest_1",
        date_responses=[
            AnswerDateResponse(
                date_candidate_id=date_candidate_ids[0],
                score=5, comment="この日程でOK"),
            AnswerDateResponse(
                date_candidate_id=date_candidate_ids[1],
                score=3, comment="調整可能"),
        ],
        preferred_budget=5000,
        preferred_area_id=area_candidate_ids[0],
        overall_comment="楽しみにしています！",
    )
    result = ParticipantService.submit_response(answer)
    print(f"{'✓' if result['status'] == 'success' else '✗'} {result['message']}")

    # ===== OrganizerService.get_managed_events =====
    print("\n[テスト4] get_managed_events")
    result = OrganizerService.get_managed_events("manager_1")
    if result["status"] == "success":
        print(f"✓ 計画中={len(result['data']['planning'])} "
              f"確定={len(result['data']['confirmed'])} "
              f"完了={len(result['data']['completed'])}")
    else:
        print(f"✗ 失敗: {result['message']}")

    # ===== OrganizerService.confirm_event =====
    print("\n[テスト5] confirm_event")
    confirmed = ConfirmedInformation(
        event_id=event_id,
        confirmed_datetime_id=date_candidate_ids[0],
        confirmed_area_id=area_candidate_ids[0],
        confirmed_shop_name="和食処 ますだ",
        confirmed_budget=5500,
        payment_destination="三菱UFJ銀行 〇〇支店 普通 1234567 マスダ タロウ",
        paypay_link="https://paypay.me/xxxx/5500",
    )
    result = OrganizerService.confirm_event(confirmed)
    print(f"{'✓' if result['status'] == 'success' else '✗'} {result['message']}")

    # ===== 確定後の状態確認 =====
    print("\n[テスト6] 確定後の状態確認")
    result = OrganizerService.get_managed_events("manager_1")
    if result["status"] == "success":
        print(f"✓ 計画中={len(result['data']['planning'])} "
              f"確定={len(result['data']['confirmed'])}")

    print("\n" + "=" * 60)
    print("✅ 全てのサービステストが正常に終了しました")
    print("=" * 60)


if __name__ == "__main__":
    main()
