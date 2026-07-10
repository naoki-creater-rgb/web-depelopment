from contextlib import contextmanager
from sqlalchemy.orm import Session
from database import SessionLocal
from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from repositories.candidate_repository import EventCandidateRepository
from repositories.response_repository import EventParticipantRepository


class UnitOfWork:
    """
    複数のRepositoryを統一されたセッションで管理
    トランザクション制御を一元化する
    """

    def __init__(self, session: Session):
        self.session = session
        self.user_repository = UserRepository(session)
        self.event_repository = EventRepository(session)
        self.candidate_repository = EventCandidateRepository(session)
        self.response_repository = EventParticipantRepository(session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストを抜ける時に自動的にcommit/rollback"""
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()

    def commit(self):
        """手動でcommit"""
        self.session.commit()

    def rollback(self):
        """手動でrollback"""
        self.session.rollback()


@contextmanager
def get_unit_of_work():
    """
    UnitOfWorkをコンテキストマネージャーで取得
    使用例：
        with get_unit_of_work() as uow:
            user = uow.user_repository.find_by_id(user_id)
            events = uow.event_repository.find_by_manager(user_id)
    """
    uow = UnitOfWork(SessionLocal())
    try:
        yield uow
        uow.session.commit()
    except Exception:
        uow.session.rollback()
        raise
    finally:
        uow.session.close()
