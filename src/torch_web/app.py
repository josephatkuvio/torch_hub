from multiprocessing.dummy import freeze_support
from flask_mail import Mail
from flask_socketio import SocketIO
from torch_web import create_app

if __name__ == "__main__":
    freeze_support()
    app = create_app()
    socketio = SocketIO(app)
    mail = Mail(app)

    app.app_context().push()
    socketio.run(app)
else:
    app = create_app()
    mail = Mail(app)

    freeze_support()
    app.app_context().push()
