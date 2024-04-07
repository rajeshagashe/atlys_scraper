from pydantic import BaseModel

class Records(BaseModel):
    scraped_count: int = 0
    updated_count: int = 0

    def save(self): #this can be overwritten to implement other storage strategies
        print(f'no of products scraped: {self.scraped_count},\nno of products updated in db: {self.updated_count}')