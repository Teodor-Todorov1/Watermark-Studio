from flask import Flask, request, jsonify, Blueprint
from PIL import Image
import base64
import io
import random
from reedsolo import RSCodec, ReedSolomonError


rsc = RSCodec(5)  # 5 ecc symbols


# Defining a blueprint
watermarking_bp = Blueprint(
    'watermarking_bp', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/watermark/static/'
)

@watermarking_bp.route('/watermark')
def index():
    return '''Server Works!<hr>
<form action="/processing" method="POST" enctype="multipart/form-data">
WM text: <input type="text" name="wm_text">
WM password: <input type="password" name="wm_pass">
<input type="file" name="image">
<button>OK</button>
</form>    
<hr>
<form action="/processingBack" method="POST" enctype="multipart/form-data">
WM length: <input type="text" name="wm_len">
WM password: <input type="password" name="wm_pass">
<input type="file" name="image">
<button>OK</button>
</form>    
'''


def generateWMPositions(rows, columns):
    posArr = [[] for i in range(rows + columns - 1)]
    center = [rows//2, columns//2]
    deltaX = 100 if rows > 600 else 50
    deltaY = 100 if columns > 600 else 50
    for i in range(center[0]-deltaX,center[0]+deltaX):
        for j in range(center[1]-deltaY,center[1]+deltaY):
            random_number = random.randint(0, 100)
            sum = i + j
            if (random_number > 33):
                if (sum % 2 == 0):
                    posArr[sum].insert(0, [i, j, random_number > 66])
                else:
                    posArr[sum].append([i, j, random_number > 66])
    return posArr


def string2bits(s=''):
    return ''.join([bin(ord(x))[2:].zfill(8) for x in s])


def bits2string(b=None):
    return ''.join([chr(int(x, 2)) for x in b])


def bytes2bits(bytes):
    return ''.join([bin(x)[2:].zfill(8) for x in bytes])


def bits2bytes(bits):
    bin_arr = bytearray()
    for x in bits:
        bin_arr.append(int(x, 2))
    return bin_arr

def encodeHamChunk(s):
    res = ''
    s = string2bits(s)
    while len(s) >= 4:
        extractPart = s[0:4]
        res += '0'+encodeHam(extractPart)
        s = s[4:]
    return bytearray(int(res, 2).to_bytes((len(res) + 7) // 8))
def encodeHam(bits):
    t1 = parityHam(bits, [0, 1, 3])
    t2 = parityHam(bits, [0, 2, 3])
    t3 = parityHam(bits, [1, 2, 3])
    return t1 + t2 + bits[0] + t3 + bits[1:]

def parityHam(s, indicies):
    sub = ""
    for i in indicies:
        sub += s[i]
    return str(sub.count("1") % 2)

def decodeHam(bitsArray):
    decodedBits = []
    #bitsArray = ['0', '1', '0', '0', '1', '1', '0', '0', '0', '0', '1', '1', '1', '1'] #test with the character g, should print 01100111
    bitsArray = bitsArray[1:]
    s = ''
    while len(bitsArray) >= 4 + 3:
        b1 = (int(bitsArray[0]) + int(bitsArray[2]) + int(bitsArray[4]) + int(bitsArray[6])) % 2
        b2 = (int(bitsArray[1]) + int(bitsArray[2]) + int(bitsArray[5]) + int(bitsArray[6])) % 2
        b3 = (int(bitsArray[3]) + int(bitsArray[4]) + int(bitsArray[5]) + int(bitsArray[6])) % 2

        b = 4 * b3 + 2 * b2 + b1

        if b == 0 or b == 1 or b == 2 or b == 4:
            s += str(bitsArray[2])+str(bitsArray[4])+str(bitsArray[5])+str(bitsArray[6])
        else:
            y = list(bitsArray)
            y[b - 1] = str((int(y[b - 1]) + 1) % 2)
            s += y[2]+ y[4]+y[5]+y[6]
        if len(s) == 8:
            decodedBits.append(s)
            s = ''
        bitsArray = bitsArray[4 + 3 + 1:]
    return decodedBits

def encodingRS(msg):
    return rsc.encode(msg)


def decodingRS(msg):
    return rsc.decode(msg)[0]


@watermarking_bp.route('/processing', methods=['POST'])
def process():
    file = request.files['image']
    i = 0
    eHam = encodeHamChunk(request.form['wm_text'])
    encStr = encodingRS(eHam)
    wm = bytes2bits(encStr)  # string2bits(str(encStr)) #"011011000110010101100100011001110110010101110010"
    with Image.open(file.stream) as img:
        random.seed(request.form['wm_pass'])  # set the seed
        width, height = img.size
        lstX = list(range(width))
        lstY = list(range(height))
        numBytes = len(wm) // 4
        usedBits = 0

        for i in range(0, numBytes):
            x = random.sample(lstX, 1)[0]
            y = random.sample(lstY, 1)[0]
            # print([x, y])
            pixel = list(img.getpixel((x, y)))
            for n in range(0, 3, 2):
                if (usedBits < len(wm)):
                    pixel[n] = pixel[n] & ~3 | int(wm[usedBits]) << 1 | int(wm[usedBits + 1])
                    usedBits += 2
            img.putpixel((x, y), tuple(pixel))
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

    return f'<img src="data:image/png;base64,{data}">'


@watermarking_bp.route('/processingBack', methods=['POST'])
def processBack():
    file = request.files['image']
    wm_len = int(request.form['wm_len'])
    extracted_bin = []
    i = 0
    c = ''
    flag = False
    with Image.open(file.stream) as img:
        width, height = img.size
        byte = []
        random.seed(request.form['wm_pass'])  # set the seed
        width, height = img.size
        lstX = list(range(width))
        lstY = list(range(height))
        numBytes = 8 * wm_len // 4
        usedBits = 0
        for i in range(0, numBytes):
            x = random.sample(lstX, 1)[0]
            y = random.sample(lstY, 1)[0]
            # print([x, y])
            pixel = list(img.getpixel((x, y)))
            for n in range(0, 3, 2):
                if (usedBits < 8 * wm_len):
                    c = "".join([c, str((pixel[n] & 2) >> 1), str(pixel[n] & 1)])
                    usedBits += 2
                    if (usedBits % 8 == 0):
                        extracted_bin.append(c)
                        c = ''
    data = bits2bytes(extracted_bin)  # bits2string(extracted_bin)
    decRS = decodingRS(data)
    return bits2string(decodeHam(bytes2bits(decRS)))

