"""One-off script to seed surgeons and this month's roster.

Names and numbers are NOT hardcoded here (so this file can be committed
without publishing anyone's real phone number). Instead, set them in
your .env as SURGEON_NAMES / SURGEON_NUMBERS (see .env.example), then
run:

    python seed.py
"""
import datetime as dt
import sys

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import OnCallSchedule, Surgeon

Base.metadata.create_all(bind=engine)

names = [n.strip() for n in settings.surgeon_names.split(",") if n.strip()]
numbers = [n.strip() for n in settings.surgeon_numbers.split(",") if n.strip()]

if not names or not numbers:
    sys.exit(
        "SURGEON_NAMES and SURGEON_NUMBERS must be set in .env before seeding "
        "(see .env.example)."
    )
if len(names) != len(numbers):
    sys.exit(
        f"SURGEON_NAMES has {len(names)} entries but SURGEON_NUMBERS has "
        f"{len(numbers)} - they must match up 1:1."
    )

SURGEONS = [{"name": name, "cell_number": number} for name, number in zip(names, numbers)]

# Simple example: one week each, rotating, starting today.
SCHEDULE_WEEKS = 8

db = SessionLocal()

existing = {s.name: s for s in db.query(Surgeon).all()}
surgeons = []
for s in SURGEONS:
    if s["name"] in existing:
        surgeons.append(existing[s["name"]])
    else:
        surgeon = Surgeon(**s)
        db.add(surgeon)
        db.flush()
        surgeons.append(surgeon)

db.query(OnCallSchedule).delete()

today = dt.date.today()
for week in range(SCHEDULE_WEEKS):
    surgeon = surgeons[week % len(surgeons)]
    start = today + dt.timedelta(weeks=week)
    end = start + dt.timedelta(days=6)
    db.add(
        OnCallSchedule(
            surgeon_id=surgeon.id,
            service="general_surgery",
            start_date=start,
            end_date=end,
        )
    )

db.commit()
print(f"Seeded {len(surgeons)} surgeons and {SCHEDULE_WEEKS} weeks of roster.")
