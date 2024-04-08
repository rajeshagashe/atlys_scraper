import os
import asyncio
import time
import random

from typing import Annotated, Union
from fastapi import APIRouter, HTTPException, Header

from ..helpers.scraper_helper import scraper_factory, scrape_website
from ..dto.dto import scraper_dto

scrape_router = APIRouter(prefix="/v1/scrape")

@scrape_router.post("/")
async def scrape(data: scraper_dto, api_key: Annotated[Union[str, None], Header()] = None):
    try:
        if api_key != os.environ.get('SCRAPE_API_KEY'):
            raise HTTPException(status_code=401, detail="Unauthorized")
        data = data.model_dump()
        session_id = f"{random.randint(1000, 9999)}_{int(time.time() * 1000)}"
        asyncio.create_task(scrape_website(data, session_id)) #not waiting for scrape job to finish loging the record to console
        return {"msg": "job successfully started", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))