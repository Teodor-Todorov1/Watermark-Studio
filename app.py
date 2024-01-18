from flask import Flask
from flask_session import Session
from datetime import timedelta
from my_app.register import registration
from my_app.watermark import watermarking
from my_app.core import core

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "123456789"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=5)
sess = Session(app)

app.register_blueprint(watermarking.watermarking_bp)
app.register_blueprint(registration.registration_bp)
app.register_blueprint(core.core_bp)
registration.oauth.init_app(app)
