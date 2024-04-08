from pydantic import BaseModel

class Records(BaseModel):
    session_id: str = ''  # this can be used to retrieve info for particular session, session_id will be sent as a response to the scrape api
    scraped_count: int = 0
    updated_count: int = 0

    def save(self): #this can be overwritten to implement other storage strategies
        print(f'no of products scraped: {self.scraped_count},\nno of products updated in db: {self.updated_count}')