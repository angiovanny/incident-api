from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Incident API is running"}
