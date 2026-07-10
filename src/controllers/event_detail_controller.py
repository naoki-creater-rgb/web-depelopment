from fastapi import APIRouter
from services.event_detail_service import EventDetailService

router = APIRouter(tags=["event_detail"])

@router.get("/event/detail")
def get_event_detail(event_id: int):
  return EventDetailService.get_event_detail(event_id)
