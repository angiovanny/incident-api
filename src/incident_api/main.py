from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, model_validator

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


class IncidentUpdate(BaseModel):
    status: IncidentStatus | None = None
    description: str | None = None

    @model_validator(mode="after")
    def validate_update_fields(self) -> "IncidentUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        if "status" in self.model_fields_set and self.status is None:
            raise ValueError("status cannot be null")

        if "description" in self.model_fields_set and self.description is None:
            raise ValueError("description cannot be null")

        return self


incidents: list[Incident] = []


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Incident API is running"}


@app.get("/incidents")
def get_incidents() -> list[Incident]:
    return incidents


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

    incidents.append(incident_return)
    return incident_return


@app.get("/incidents/{incident_id}")
def get_incident_by_id(incident_id: UUID) -> Incident:
    for incident in incidents:
        if incident.id == incident_id:
            return incident

    raise HTTPException(
        status_code=404,
        detail="Incident not found",
    )


@app.patch("/incidents/{incident_id}")
def incident_update(
    incident_id: UUID,
    incident_update: IncidentUpdate,
) -> Incident:
    for incident in incidents:
        if incident.id == incident_id:
            if incident_update.status is not None:
                incident.status = incident_update.status

            if incident_update.description is not None:
                incident.description = incident_update.description

            return incident

    raise HTTPException(
        status_code=404,
        detail="Incident not found",
    )
