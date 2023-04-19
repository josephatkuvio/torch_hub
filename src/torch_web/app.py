from multiprocessing.dummy import freeze_support
from flask_mail import Mail
from flask_socketio import SocketIO
from torch_web import create_app
from prefect import context


app = create_app()
socketio = SocketIO(app)

if __name__ == "__main__":
    freeze_support()
    socketio.init_app(app, cors_allowed_origins="*")
    mail = Mail(app)

    app.app_context().push()
    context.socketio = socketio
    socketio.run(app)
else:
    freeze_support()
    socketio.init_app(app, cors_allowed_origins="*")
    mail = Mail(app)

    app.app_context().push()
    context.socketio = socketio
