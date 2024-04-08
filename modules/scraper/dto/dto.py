from pydantic import BaseModel, Field
from typing import Union

class Retries(BaseModel):
    count: int = Field(default=1, le=10, ge=1) 
    interval: int = Field(default=5, le=10, gt=0)

class ScraperDTO(BaseModel):
    url: str
    page_count: Union[int, None] = Field(None, ge=1)
    proxy_string: Union[str, None] = None
    retries: Retries = {}