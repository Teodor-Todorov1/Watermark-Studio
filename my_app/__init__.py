from flask import Flask

app = Flask(__name__)

from .register import registration
from .watermark import watermarking

app.register_blueprint(watermarking.watermarking_bp)
app.register_blueprint(registration.registration_bp)
