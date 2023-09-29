from PIL import Image
import base64
import io
import random
from reedsolo import RSCodec, ReedSolomonError
from flask import Blueprint, flash, redirect, render_template, request, session, url_for, Flask, jsonify, send_file

from my_app.watermark.wm_class import WM

wm = WM()

# Defining a blueprint
watermarking_bp = Blueprint(
    'watermarking_bp', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/watermark/static/'
)


@watermarking_bp.route('/watermark')
def index():
    return render_template("watermarking.html")


@watermarking_bp.route('/processing', methods=['POST'])
def process():
    file = request.files['image']
    with Image.open(file.stream) as img:
        wm.encode(img, request.form['wm_text'])
    buffer = io.BytesIO()
    img.save(buffer, 'png')
    buffer.seek(0)
    data = buffer.read()
    data = base64.b64encode(data).decode()
    # return jsonify({
    #            'msg': 'success',
    #            'size': [img.width, img.height],
    #            'format': img.format,
    #            'img': data
    #       })

    # with io.BytesIO() as buffer:
    #    img.save(buffer, 'png')
    #    buffer.seek(0)
    #    temp_image_path = 'temp_image.png'
    #    with open(temp_image_path, 'wb') as temp_file:
    #        temp_file.write(buffer.read())

    return render_template('download.html', img_data=data)


@watermarking_bp.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)


@watermarking_bp.route('/processingBack', methods=['POST'])
def processBack():
    file = request.files['image_back']
    with Image.open(file.stream) as img:
        return wm.decode(img)
