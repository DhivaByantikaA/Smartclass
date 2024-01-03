# non docker
# install
 pip install -r requirements.txt

# run
uvicorn app.main:app --host=0.0.0.0 --reload
uvicorn app.main:app --reload --host=0.0.0.0 --port=8000 --workers=1 --limit-concurrency=5

# non docker
# install
 pip install -r requirements.txt

# check
open https://localhost:8000/docs


# get local key
python -m tinytuya wizard

# Authorization 
    "apiKey": "85g47eeeb6j5zz1fpg0r",
    "apiSecret": "43e369cb8e7b47d48f33acd0b689b689",
    "apiRegion": "us",
    "apiDeviceID": "ebc2baff541c8eb67cnv8z"


# Rtsp scan
# a subnet
rtspscanner -m scan -c admin:pahlawan10 -a 192.168.4.0/24

# single IP 
rtspscanner -m scan -c admin:pahlawan10 -a 192.168.4.189

# OCR RADEA

install postgresql
install nodered
install miniconda

install flow flows-ocr-radea.json

python -m pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
pip install "paddleocr>=2.0.1" --upgrade PyMuPDF==1.21.1

copy .env.example ke .env

isi .env
    yolo_enable=false
    vision_enable=true
    GOOGLE_APPLICATION_CREDENTIALS="desk-iot-1bec2fd20d96-vision-iot.json"

minta ke admin desk-iot-1bec2fd20d96-vision-iot.json taruh di folder project

uvicorn app.main:app --host=0.0.0.0 --reload
