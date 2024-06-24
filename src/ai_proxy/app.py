import asyncio
import glob
import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, Form, BackgroundTasks
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from starlette.requests import Request

from ai_proxy.ai import Prompt
from ai_proxy.settings import settings

app = FastAPI()

logger.info("APP SETTINGS:\n" + "\n".join(f"{k}: {v}" for k, v in settings.dict().items()))


class Query(BaseModel):
    role: str = "user"
    message: str


@app.post("/")
async def home(query: Query):
    p = Prompt()
    return {
        "response": p.query(**query.dict())
    }
