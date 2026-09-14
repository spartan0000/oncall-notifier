import datetime as dt

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Surgeon(Base):
    __tablename__ = "surgeons"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    cell_number = Column(String, nullable=False)  # E.164 format, e.g. +6421xxxxxxx
    active = Column(Boolean, default=True, nullable=False)

    schedule_entries = relationship("OnCallSchedule", back_populates="surgeon")


class OnCallSchedule(Base):
    __tablename__ = "oncall_schedule"

    id = Column(Integer, primary_key=True)
    surgeon_id = Column(Integer, ForeignKey("surgeons.id"), nullable=False)
    service = Column(String, nullable=False, default="general_surgery")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    surgeon = relationship("Surgeon", back_populates="schedule_entries")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    sender_name = Column(String, nullable=False)
    surgeon_id = Column(Integer, ForeignKey("surgeons.id"), nullable=False)
    message_body = Column(Text, nullable=False)
    sent_at = Column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.timezone.utc),
        nullable=False,
    )
    twilio_sid = Column(String, nullable=True)
    twilio_status = Column(String, nullable=True)
    error = Column(Text, nullable=True)

    surgeon = relationship("Surgeon")
