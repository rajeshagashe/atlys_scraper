# atlys_scraper
scraper bot 

Python Version - 3.9.6 (app may not work properly for lower versions)

for setup run one_time_setup.sh (this also activates the virtual env)
to run the application execute `source run.sh` inside the folder where this repo is cloned

visit http://localhost:8000/docs when the application is running to see the api contracts


example request - 
```
curl --location 'localhost:8000/v1/scrape' \
--header 'Api-Key: scrape_api_key' \
--header 'Content-Type: application/json' \
--data '{
    "url": "https://dentalstall.com/shop/",
    "retries": {
        "count": 5,
        "interval": 2
    },
    "page_count": 15
}'
```
