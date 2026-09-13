# On-call notifier (MVP)

Minimal FastAPI + Postgres + Twilio app for one surgical service to notify
whoever is currently on call by SMS, without sending any patient
information in the message body.

## Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Have a local Postgres running, then:
createdb oncall
cp .env.example .env   # edit DATABASE_URL / Twilio creds

python seed.py          # edit the SURGEONS list in seed.py first!
uvicorn app.main:app --reload
```

Open http://localhost:8000 - enter your name, hit "Send notification".

With `DRY_RUN=true` (the default) no real SMS is sent; the app logs what
it *would* send to the console and still records a `notifications` row,
so you can test the whole flow before wiring up real Twilio credentials.

## What it does

- `GET /oncall` - looks up who's on call today from `oncall_schedule`.
- `POST /notify` - sends them an SMS along the lines of:
  "Non-urgent transfer inquiry. From David. Please call back when free."
  and logs the attempt (sender, surgeon, timestamp, delivery status) in
  the `notifications` table.

No patient-identifying free text is accepted anywhere in the request -
the `reason` field is meant for something generic like "non-urgent
transfer inquiry", not clinical details. Keep it that way if you want to
stay clear of handling health information in the message content.

## Editing the roster

For now, `seed.py` is the roster editor - open it, put in the three real
names/numbers and adjust the rotation logic, then re-run
`python seed.py` to reset the schedule. A small web form for editing the
roster is a natural next step once the notify flow itself is proven out.

## Not included yet (intentionally, for a v1)

- Escalation to a backup surgeon if there's no reply/delivery.
- Voice call fallback for urgent cases (keep doing that by phone).
- Authentication on the endpoints - fine for a local trial with 3 people
  on a private network, not fine before wider or remote deployment.
- Two-way SMS handling (inbound replies aren't processed).
