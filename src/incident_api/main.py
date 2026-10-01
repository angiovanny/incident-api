from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class IncidentPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentType(str, Enum):
    HARDWARE = "HARDWARE"
    SOFTWARE = "SOFTWARE"
    NETWORK = "NETWORK"
    SECURITY = "SECURITY"


class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class IncidentCreate(BaseModel):
    type: IncidentType
    priority: IncidentPriority
    subject: str
    description: str
    user_id: int


class Incident(IncidentCreate):
    status: IncidentStatus
    id: UUID
    created_at: datetime


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Incident API is running"}


@app.get("/incidents")
def get_incidents() -> list:
    return []


@app.post("/incidents", status_code=201)
def create_incident(incident: IncidentCreate) -> Incident:
    incident_return = Incident(
        type=incident.type,
        priority=incident.priority,
        subject=incident.subject,
        description=incident.description,
        user_id=incident.user_id,
        status=IncidentStatus.OPEN,
        id=uuid4(),
        created_at=datetime.now(UTC),
    )
    return incident_return
