import datetime as dt

from pydantic import BaseModel, Field


class OnCallOut(BaseModel):
    surgeon_id: int
    name: str
    cell_number: str
    service: str


class NotifyRequest(BaseModel):
    sender_name: str = Field(..., min_length=1, max_length=100)
    reason: str = Field(
        default="Non-urgent transfer inquiry",
        max_length=200,
        description="Short, non-clinical reason shown in the SMS. Do not include patient identifiers.",
    )
    service: str = "general_surgery"


class NotifyResponse(BaseModel):
    notification_id: int
    surgeon_name: str
    status: str
    message_body: str
