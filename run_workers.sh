mkdir -p logs

celery -A core worker -Q asmr_cutting --concurrency=1 --loglevel=info > logs/celery_asmr.log 2>&1 &
PID1=$!

celery -A core worker -Q default --concurrency=4 --loglevel=info > logs/celery_default.log 2>&1 &
PID2=$!

echo "Воркеры запущены. Нажмите Ctrl+C чтобы их остановить."

trap "echo 'Остановка воркеров...'; kill $PID1 $PID2; exit" SIGINT

wait