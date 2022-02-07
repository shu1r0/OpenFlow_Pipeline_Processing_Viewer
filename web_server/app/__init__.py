from flask import Flask
from flask_socketio import SocketIO


app = Flask(__name__, static_folder='./static/', template_folder='./templates')

app.config.from_object('app.configuration.DevelopmentConfig')
# app.config.from_object('configuration.TestingConfig')

socketio = SocketIO(app, async_mode=None)

from src.web_server.app import views
