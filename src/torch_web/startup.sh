# For Azure startup with websocket support
gunicorn --worker-class eventlet -w 1 --bind=0.0.0.0 --timeout 600 app:app