from pydantic import BaseModel


class CreateNewEvent(BaseModel):
    manager_id: str
    event_name: str
    response_deadline: str
    description: str
    candidate_dates: list[str]
    candidate_areas: list[str]
    desired_budget: int
    participants: list[str]


class ConfirmedInformation(BaseModel):
    event_id: str
    confirmed_datetime_id: str
    confirmed_area_id: str
    confirmed_shop_name: str
    confirmed_budget: float
    payment_destination: str
    paypay_link: str = None
