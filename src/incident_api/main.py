from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Incident API is running"}


@app.get("/incidents")
def get_incidents() -> list:
    return []
