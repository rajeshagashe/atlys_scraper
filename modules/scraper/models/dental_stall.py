import json
from pydantic import BaseModel

class DentalStallProdpuctCatalogue(BaseModel):
    product_title: str = ""
    product_price: str = ""
    path_to_image: str = "" #considering combination of all three to be the unqiue id

    async def upsert(self) -> None: # this method can be overwritten to write to a differnet db
        filename = 'database.json'

        json_data = self.model_dump_json()
        
        try:
            with open(filename, "r") as file:
                database = json.load(file)
        except FileNotFoundError:
            database = []

        record_index = None
        for i, db_record in enumerate(database):
            db_record = json.loads(db_record)
            if db_record.get("path_to_image") == self.path_to_image \
                and db_record.get("product_title") == self.product_title\
                and db_record.get("product_price") == self.product_price:
                record_index = i
                break

        if record_index is not None:
            database[record_index] = str(json_data)
        else:
            database.append(str(json_data))

        with open(filename, "w") as file:
            json.dump(database, file, indent=4)