celery -A core worker -Q asmr_cutting --concurrency=1 --loglevel=info
celery -A core worker -Q default --concurrency=4 --loglevel=info