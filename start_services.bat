@echo off
REM Start Django (Gunicorn), Celery worker, and Celery beat, each in its own window

start "Django (Gunicorn)" cmd /k gunicorn readmore.wsgi:application
start "Celery Worker" cmd /k celery -A readmore worker --loglevel=info
start "Celery Beat" cmd /k celery -A readmore beat --loglevel=info

echo All services started in separate windows. Press any key to exit this window.
pause >nul
