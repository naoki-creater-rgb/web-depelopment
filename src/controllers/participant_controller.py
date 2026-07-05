from fastapi import APIRouter
from services.participant_service import ParticipantService
from controllers.models.participant_models import ParticipantCreateAnswer

router = APIRouter(tags=["participant"])

@router.get("/participant/events")
def get_participant_events(participant_id: str):
  return ParticipantService.get_participating_events(participant_id)

@router.post("/participant/create/answer")
def create_answer(participant_create_answer: ParticipantCreateAnswer):
  return ParticipantService.submit_response(participant_create_answer)