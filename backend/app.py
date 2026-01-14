from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import Literal
from pathlib import Path
import json

### Config
DATA_FILE = Path(__file__).resolve().parent / "data" / "tickets.json"

### Models
TicketStatus = Literal["open", "in_progress", "closed"]

class Ticket(BaseModel):
    id: str
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    status: TicketStatus
    created_at: datetime

class TicketCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    status: TicketStatus = "open"

class StatusPatch(BaseModel):
    status: TicketStatus

### Data access
def load_tickets():
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return [Ticket(**item) for item in raw]

ticket_store: dict[str, Ticket] = {t.id: t for t in load_tickets()}

def next_id() -> str:
    if not ticket_store:
        return "1"
    return str(max(int(ticket_id) for ticket_id in ticket_store.keys()) + 1)

def save_tickets():
    payload = [t.model_dump(mode="json") for t in ticket_store.values()]
    DATA_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

### API
app = FastAPI(title="Ticketing API")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/tickets", status_code=200, response_model=list[Ticket])
async def get_tickets():
    return sorted(ticket_store.values(), key=lambda t: t.created_at, reverse=True)

@app.post("/tickets", status_code=201, response_model=Ticket)
async def create_ticket(ticket: TicketCreate):
    # check title uniqueness
    if any(ticket.title.casefold() == t.title.casefold() for t in ticket_store.values()):
        raise HTTPException(status_code=409, detail=f"Ticket with title '{ticket.title}' already exists")

    new_ticket = Ticket(
            id=next_id(),
            title=ticket.title,
            description=ticket.description,
            status=ticket.status,
            created_at=datetime.now(timezone.utc),
        )
    ticket_store[new_ticket.id] = new_ticket
    save_tickets()
    return new_ticket

@app.patch("/tickets/{ticket_id}", status_code=204)
async def patch_ticket_status(ticket_id: str, patch: StatusPatch):
    ticket = ticket_store.get(ticket_id)
    if ticket is None:
        raise HTTPException(404, detail=f"Ticket {ticket_id} not found")

    updated = ticket.model_copy(update={"status": patch.status})
    ticket_store[ticket_id] = updated
    save_tickets()
    return
