import os
import asyncio

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
        asyncio.create_task(scrape_website(data)) #not waiting for scrape job to finish loging the record to console
        return {"msg": "job successfully started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))