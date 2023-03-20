from fastapi import FastAPI, Depends, HTTPException
from typing import Dict
from pydantic import BaseModel
from typing import List, Optional
from src.api.api_class import Execution, Events, LOGIN, \
    LOGOUT
import webbrowser

app = FastAPI()

clients: Dict[str, any] = {}


class BotParameters(BaseModel):
    symbol: str
    timeframe: str = "5Min"
    rsi_period: int = 14
    rsi_upper: int = 70
    rsi_lower: int = 30


class Symbol(BaseModel):
    symbol: str


class Percent(BaseModel):
    percent: float


def get_client(client_id: str):
    client_api = clients.get(client_id)
    if not client_api:
        raise HTTPException(status_code=400, detail="Invalid client ID")
    return client_api


@app.post("/login/")
def login(key: str, secret: str):
    client_api = LOGIN(key, secret)
    client_id = str(id(client_api))
    clients[client_id] = client_api  # Store the client instance in the clients dictionary
    return {"result": "success", "client_id": client_id}


# @app.post("/logout/")
# def logout():
#     LOGOUT()
#     return {"result": "success"}


@app.post("/execution/create_bot/")
def create_bot(client_id: str, bot_params: BotParameters, client=Depends(get_client)):
    execution = Execution(client)
    execution.create_bot(**bot_params.dict())
    return {"result": "success"}


@app.post("/events/show_logs/")
def show_logs(symbol: Symbol):
    events = Events(symbol.symbol)
    logs_text = events.show_logs()
    return {"result": "success", "logs": logs_text}


@app.get("/")
def root():
    return {
        "message": "Welcome to the FastAPI backend! Use the provided endpoints for managing bots and events."
    }


def open_docs():
    docs_url = "http://localhost:8000/docs"
    webbrowser.open(docs_url)


if __name__ == "__main__":
    import uvicorn

    open_docs()
    uvicorn.run(app, host="0.0.0.0", port=8000)
