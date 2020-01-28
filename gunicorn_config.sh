gunicorn -D --workers=3 --bind=0.0.0.0:5000 --log-file=flasklog.log --pid=gunicorn.pid --log-level=debug app:app

