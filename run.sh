python3 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app