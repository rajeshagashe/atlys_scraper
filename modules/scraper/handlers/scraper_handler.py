import os
import asyncio
import time
import random

from typing import Annotated, Union
from fastapi import APIRouter, HTTPException, Header

from ..helpers.scraper_helper import scrape_website
from ..dto.dto import ScraperDTO

scrape_router = APIRouter(prefix="/v1/scrape")

@scrape_router.post("/")
async def scrape(data: ScraperDTO, api_key: Annotated[Union[str, None], Header()] = None):
    try:
        if api_key != os.environ.get('SCRAPE_API_KEY'):
            raise HTTPException(status_code=401, detail="Unauthorized")
        data = data.model_dump()
        session_id = f"{random.randint(1000, 9999)}_{int(time.time() * 1000)}"
        asyncio.create_task(scrape_website(data, session_id)) #not waiting for scrape job to finish loging the record to console
        return {"msg": "job successfully started", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))