from enum import Enum

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


class IncidentCreate(BaseModel):
    type: IncidentType
    priority: IncidentPriority
    subject: str
    description: str
    user_id: int


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Incident API is running"}


@app.get("/incidents")
def get_incidents() -> list:
    return []


@app.post("/incidents", status_code=201)
def create_incident(incident: IncidentCreate) -> IncidentCreate:
    return incident
