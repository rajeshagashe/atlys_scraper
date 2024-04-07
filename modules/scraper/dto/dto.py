from pydantic import BaseModel, Field
from typing import Union

class Retries(BaseModel):
    count: int = Field(default=1, le=10, ge=1) 
    interval: int = Field(default=5, le=10, gt=0)

class scraper_dto(BaseModel):
    url: str
    start_page: int = Field(default=1, ge=1)
    end_page: int = Field(default=1, le=100) # hard-coding maximum value to save time. Should be made configurable
    proxy_string: Union[str, None] = None
    retries: Retries = {}