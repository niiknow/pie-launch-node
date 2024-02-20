from datetime import date, datetime

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    """healthcheck endpoint

    Returns:
        string: OK
    """
    return "OK"


@app.get("/build")
async def build(tenant: str, key: str, start: date = date.today()):
    return {"message": "Hello World"}
