from flask import Flask
from .blueprint import BLUEPRINT

app = Flask(__name__)

app.config.from_envvar('QREMISER_CONFIG', silent=True)

app.register_blueprint(BLUEPRINT)
