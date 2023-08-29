from flask import Flask
from my_app.watermark.watermarking import watermarking_bp
from my_app.register.registration import registration_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(watermarking_bp)
app.register_blueprint(registration_bp)

if __name__ == '__main__':
    app.run()
