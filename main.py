from fastapi import FastAPI
from dotenv import load_dotenv
from modules.scraper.handlers.scraper_handler import scrape_router 

load_dotenv()

app = FastAPI()

app.include_router(scrape_router)