from fastapi import FastAPI
from services.event_detail_service import EventDetailService

app = FastAPI()

@app.get("/event/detail")
def get_event_detail(event_id: int):
  return EventDetailService.get_event_detail(event_id)
