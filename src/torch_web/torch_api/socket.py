import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)

def init(app):
    app.mount("/ws", socket_app)
    return sio

 