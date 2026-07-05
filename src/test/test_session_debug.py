#!/usr/bin/env python3
"""
セッション管理のデバッグ：Detached オブジェクトにどうアクセスできるか検証
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from database import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from models.user_entity import User
from models.event_entity import Event, Status
from database import get_session

def test_detached_access():
    """Detached オブジェクトへのアクセスをテスト"""

    print("=" * 70)
    print("セッション管理デバッグ：Detached オブジェクトへのアクセス")
    print("=" * 70)

    # テーブル作成
    from sqlalchemy import text
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    db.execute(text("DELETE FROM events"))
    db.execute(text("DELETE FROM users"))
    db.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    db.commit()

    # テストユーザー作成
    u = User(user_id="test_user", password_hash="hash", display_name="テストユーザー")
    db.add(u)
    db.commit()
    db.close()

    print("\n[シナリオ] リポジトリでセッション管理 → Detached オブジェクト返却")
    print("-" * 70)

    # パターン1：refresh後に return
    print("\n【パターン1】flush + refresh後に return")
    print("-" * 70)

    def pattern1_refresh():
        """flush + refresh後に return"""
        with get_session() as db:
            event = Event(
                manager_id="test_user",
                event_name="テストイベント1",
                response_deadline=datetime(2026, 8, 1, 19, 0),
                description="説明",
                status="planning"
            )
            db.add(event)
            db.flush()
            db.refresh(event)  # ← データベースから再度読み込む

            print(f"セッション内:")
            print(f"  - event: {event}")
            print(f"  - event_id: {event.event_id}")
            print(f"  - event_name: {event.event_name}")
            print(f"  - id in object.__dict__: {'event_id' in event.__dict__}")

            return event
        # ← セッション終了

    event1 = pattern1_refresh()

    print(f"\nセッション外:")
    print(f"  - event: {event1}")
    print(f"  - event_id in __dict__: {'event_id' in event1.__dict__}")

    # セッション外でアクセス試行
    try:
        # 実は、flush/refresh後なら、スカラー属性にはアクセスできる
        event_id = event1.event_id
        print(f"  ✅ event_id = {event_id}  (アクセス成功！)")
    except Exception as e:
        print(f"  ❌ event_id アクセス失敗: {e}")

    try:
        event_name = event1.event_name
        print(f"  ✅ event_name = {event_name}  (アクセス成功！)")
    except Exception as e:
        print(f"  ❌ event_name アクセス失敗: {e}")

    # パターン2：flush のみ（refresh なし）
    print("\n【パターン2】flush のみ（refresh なし）で return")
    print("-" * 70)

    def pattern2_no_refresh():
        """flush のみで return"""
        with get_session() as db:
            event = Event(
                manager_id="test_user",
                event_name="テストイベント2",
                response_deadline=datetime(2026, 8, 2, 19, 0),
                description="説明2",
                status="planning"
            )
            db.add(event)
            db.flush()
            # refresh なし

            print(f"セッション内:")
            print(f"  - event_id: {event.event_id}")
            print(f"  - event_name: {event.event_name}")

            return event
        # ← セッション終了

    event2 = pattern2_no_refresh()

    print(f"\nセッション外:")
    try:
        event_id = event2.event_id
        print(f"  ✅ event_id = {event_id}  (アクセス成功！)")
    except Exception as e:
        print(f"  ❌ event_id アクセス失敗: {type(e).__name__}: {e}")

    # パターン3：リレーションシップアクセス
    print("\n【パターン3】リレーションシップへのアクセス")
    print("-" * 70)

    def pattern3_relationship():
        """manager（User）リレーションシップアクセス試行"""
        with get_session() as db:
            event = Event(
                manager_id="test_user",
                event_name="テストイベント3",
                response_deadline=datetime(2026, 8, 3, 19, 0),
                description="説明3",
                status="planning"
            )
            db.add(event)
            db.flush()
            db.refresh(event)

            print(f"セッション内:")
            print(f"  - event.manager: {event.manager}")
            print(f"  - event.manager.display_name: {event.manager.display_name}")

            return event
        # ← セッション終了

    event3 = pattern3_relationship()

    print(f"\nセッション外:")
    try:
        # スカラー属性アクセス
        event_id = event3.event_id
        print(f"  ✅ event_id = {event_id}  (OK)")
    except Exception as e:
        print(f"  ❌ event_id: {type(e).__name__}: {e}")

    try:
        # リレーションシップアクセス（これはエラーになる）
        manager = event3.manager
        print(f"  ✅ event.manager = {manager}")
    except Exception as e:
        print(f"  ❌ event.manager: {type(e).__name__}")
        print(f"     (リレーションシップは遅延ローディングが必要)")

    print("\n" + "=" * 70)
    print("結論")
    print("=" * 70)
    print("""
✅ スカラー属性（event_id, event_name など）はアクセス可能
   理由：flush/refresh後、値がメモリに読み込まれているため

❌ リレーションシップ（event.manager など）はアクセス不可
   理由：遅延ローディング（lazy loading）が必要で、セッションが必要

⚠️  つまり、ORM の実装によって、セッション外でもアクセスできる部分と
   アクセスできない部分が混在している
    """)

if __name__ == "__main__":
    test_detached_access()
