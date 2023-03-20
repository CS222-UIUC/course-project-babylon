from fastapi import FastAPI, Depends, HTTPException, APIRouter
from typing import Dict
from pydantic import BaseModel
from typing import List, Optional
from src.api.api_class import Execution, Events, LOGIN, LOGOUT
import webbrowser
import uvicorn

app = FastAPI()
login_router = APIRouter(prefix="/Login", tags=["Login/Logout"])
execution_router = APIRouter(prefix="/execution", tags=["Execution"])
events_router = APIRouter(prefix="/events", tags=["Events"])

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


@login_router.post("/login/")
def login(key: str, secret: str):
    client_api = LOGIN(key, secret)
    client_id = str(id(client_api))
    clients[client_id] = client_api  # Store the client instance in the clients dictionary
    return {"result": "success", "client_id": client_id}


@login_router.post("/logout/")
def logout():
    clients.clear()
    return {"result": "success"}


@execution_router.post("/create_bot/")
def create_bot(client_id: str, bot_params: BotParameters, client=Depends(get_client)):
    execution = Execution(client)
    execution.create_bot(**bot_params.dict())
    return {"result": "success"}


@events_router.get("/show_logs/")
def show_logs(symbol: Symbol):
    events = Events(symbol.symbol)
    logs_text = events.show_logs()
    return {"result": "success", "logs": logs_text}


@execution_router.post("/set_account/")
def set_account(client=Depends(get_client)):
    execution = Execution(client)
    execution.set_account()
    return {"result": "success"}


@execution_router.get("/get_account_cash/")
def get_account_cash(client=Depends(get_client)):
    execution = Execution(client)
    cash = execution.get_account_cash()
    return {"result": "success", "cash": cash}


@execution_router.post("/set_cash_to_spend/")
def set_cash_to_spend(percent: Percent, client=Depends(get_client)):
    execution = Execution(client)
    execution.set_cash_to_spend(percent.percent)
    return {"result": "success"}


@execution_router.post("/add_symbol/")
def add_symbol(symbol: Symbol, client=Depends(get_client)):
    execution = Execution(client)
    execution.add_symbol(symbol.symbol)
    return {"result": "success"}


@execution_router.get("/get_symbol/")
def get_symbols(client=Depends(get_client)):
    execution = Execution(client)
    symbols = execution.get_symbols()
    return {"result": "success", "symbols": symbols}


@execution_router.post("/delete_symbol/")
def delete_symbol(symbol: Symbol, client=Depends(get_client)):
    execution = Execution(client)
    execution.delete_symbol(symbol.symbol)
    return {"result": "success"}


@execution_router.post("/start_bot/")
def start_bot(symbol: Symbol, client=Depends(get_client)):
    execution = Execution(client)
    execution.start_bot(symbol.symbol)
    return {"result": "success"}


@execution_router.post("/pause_bot/")
def pause_bot(symbol: Symbol, client=Depends(get_client)):
    execution = Execution(client)
    execution.pause_bot(symbol.symbol)
    return {"result": "success"}


@execution_router.post("/reset_bot/")
def reset_bot(symbol: Symbol, client=Depends(get_client)):
    execution = Execution(client)
    execution.reset_bot(symbol.symbol)
    return {"result": "success"}


@execution_router.post("/start_all_bot/")
def start_all_bots(client=Depends(get_client)):
    execution = Execution(client)
    execution.start_all_bots()
    return {"result": "success"}


@execution_router.post("/pause_all_bot/")
def pause_all_bots(client=Depends(get_client)):
    execution = Execution(client)
    execution.pause_all_bots()
    return {"result": "success"}


@execution_router.post("/reset_all_bot/")
def reset_all_bots(client=Depends(get_client)):
    execution = Execution(client)
    execution.reset_all_bots()
    return {"result": "success"}


@execution_router.get("/get_user_info/")
def get_user_info(client=Depends(get_client)):
    execution = Execution(client)
    user_info = execution.get_user_info()
    return {"result": "success", "user_info": user_info}


def open_docs():
    docs_url = "http://localhost:8888/docs"
    webbrowser.open(docs_url)


if __name__ == "__main__":
    app.include_router(login_router)
    app.include_router(execution_router)
    app.include_router(events_router)
    open_docs()
    uvicorn.run(app, host="0.0.0.0", port=8888)
