import datetime as dt

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Notification, OnCallSchedule, Surgeon
from app.schemas import NotifyRequest, NotifyResponse, OnCallOut
from app.sms import send_sms

Base.metadata.create_all(bind=engine)

app = FastAPI(title="On-Call Notifier")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


def _current_oncall(db: Session, service: str) -> Surgeon:
    today = dt.date.today()
    entry = (
        db.query(OnCallSchedule)
        .filter(
            OnCallSchedule.service == service,
            OnCallSchedule.start_date <= today,
            OnCallSchedule.end_date >= today,
        )
        .first()
    )
    if entry is None:
        raise HTTPException(404, f"No on-call surgeon found for '{service}' today ({today}).")
    surgeon = db.get(Surgeon, entry.surgeon_id)
    if surgeon is None or not surgeon.active:
        raise HTTPException(404, "Scheduled surgeon record is missing or inactive.")
    return surgeon


@app.get("/oncall", response_model=OnCallOut)
def get_oncall(service: str = "general_surgery", db: Session = Depends(get_db)):
    surgeon = _current_oncall(db, service)
    return OnCallOut(
        surgeon_id=surgeon.id,
        name=surgeon.name,
        cell_number=surgeon.cell_number,
        service=service,
    )


@app.post("/notify", response_model=NotifyResponse)
def notify_oncall(req: NotifyRequest, db: Session = Depends(get_db)):
    surgeon = _current_oncall(db, req.service)

    body = (
        f"{req.reason}. From {req.sender_name}. "
        f"Please call back when free. (Automated on-call notice, no patient details included.)"
    )

    result = send_sms(surgeon.cell_number, body)

    notification = Notification(
        sender_name=req.sender_name,
        surgeon_id=surgeon.id,
        message_body=body,
        twilio_sid=result.sid,
        twilio_status=result.status,
        error=result.error,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    if result.status == "failed":
        raise HTTPException(502, f"SMS failed to send: {result.error}")

    return NotifyResponse(
        notification_id=notification.id,
        surgeon_name=surgeon.name,
        status=result.status,
        message_body=body,
    )
