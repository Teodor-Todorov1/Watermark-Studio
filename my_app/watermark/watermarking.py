from PIL import Image
import base64
import io
import random
from reedsolo import RSCodec, ReedSolomonError
from flask import Blueprint, flash, redirect, render_template, request, session, url_for, Flask, jsonify, send_file
import cv2
import numpy as np

from my_app.watermark.wm_class import WM

wm = WM()

# Defining a blueprint
watermarking_bp = Blueprint(
    'watermarking_bp', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/watermark/static/'
)

#Text Watermark
@watermarking_bp.route('/textWatermark')
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

#Image Watermark

@watermarking_bp.route('/imageWatermark')
def imqgeIndex():
    return  render_template("imageWatermarking.html")

# Encryption function
@watermarking_bp.route('/processingImage', methods=['POST'])
def encrypt():
    if request.method == 'POST':
        # Read the uploaded images and convert them to NumPy arrays
        img1_bytes = request.files['image1'].read()
        img2_bytes = request.files['image2'].read()

        img1_np = cv2.imdecode(np.frombuffer(img1_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
        img2_np = cv2.imdecode(np.frombuffer(img2_bytes, np.uint8), cv2.IMREAD_UNCHANGED)

        for i in range(img2_np.shape[0]):
            for j in range(img2_np.shape[1]):
                for l in range(3):
                    v1 = format(img1_np[i][j][l], '08b')
                    v2 = format(img2_np[i][j][l], '08b')

                    v3 = v1[:4] + v2[:4]

                    img1_np[i][j][l] = int(v3, 2)

        # Encode the result image to base64 and return it
        result_img_bytes = cv2.imencode('.png', img1_np)[1].tobytes()
        data = base64.b64encode(result_img_bytes).decode()

        return f'<img src="data:image/png;base64,{data}">'

# Decryption function
@watermarking_bp.route('/processingImageBack', methods=['POST'])
def decrypt():
    if request.method == 'POST':
        # Read the uploaded image as a base64 encoded string
        img_base64 = request.files['image'].read()

        img = cv2.imdecode(np.frombuffer(img_base64, np.uint8), cv2.IMREAD_UNCHANGED)
        # Perform the decryption on the uploaded image
        width = img.shape[0]
        height = img.shape[1]

        img1 = np.zeros((width, height, 3), np.uint8)
        img2 = np.zeros((width, height, 3), np.uint8)

        for i in range(width):
            for j in range(height):
                for l in range(3):
                    v1 = format(img[i][j][l], '08b')
                    v2 = v1[:4] + chr(random.randint(0, 1) + 48) * 4
                    v3 = v1[4:] + chr(random.randint(0, 1) + 48) * 4

                    # Appending data to img1 and img2
                    img1[i][j][l] = int(v2, 2)
                    img2[i][j][l] = int(v3, 2)

        # Return the decrypted images as separate image responses
        img1_bytes = cv2.imencode('.png', img1)[1].tobytes()
        img2_bytes = cv2.imencode('.png', img2)[1].tobytes()

        data1 = base64.b64encode(img1_bytes).decode()
        data2 = base64.b64encode(img2_bytes).decode()

        return (f'<img src="data:image/png;base64,{data1}"'
                f'><img src="data:image/png;base64,{data2}">')
