import os

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
        await scrape_website(data)
        return {"api_key": api_key, "env": os.environ.get('SCRAPE_API_KEY')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))