from googleapiclient.http import *
from linebot.models import *
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from flask import Flask, request, abort
from googleDrive.Google import Create_Service
import numpy as np
import os
import string
import random
import cv2
import shutil
import mimetypes
import time
import json

CLIENT_SECRET_FILE = 'line-bot-tutorial-master\googleDrive\credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

app = Flask(__name__)

line_bot_api = LineBotApi(
    'bpg1dF/G8Fs8b/7TgrsVtKfZWobcKnYlUhE5Z66Qv5tpihHwDP1YN6SHR5RhBuVP4nAmR7IboDyIu2mp971jdQntGuuEhjwb3zrX9+zgU1AUvxfqhGrGk6MNOhpxpjBcBML9PmJVm3nz6zsJTBQ0RgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('6ef05fe71973294e9b92400cfa891486')


def FILE_EXT(FILE_NAME, FILE_EXTENSION):
    FOLDERS_ID = '1YzuAIUYjXh2M14-59q6ZpgtU-BNXKeo5'
    MINME_TYPE = ['application/pdf', 'application/msword',
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if FILE_EXTENSION == 'pdf':
        for i, j in zip(FILE_NAME, MINME_TYPE[0]):
            file_metadata = {
                'name': FILE_NAME,
                'parents': [FOLDERS_ID]
            }
            media = MediaFileUpload(
                'line-bot-tutorial-master\static/' + FILE_NAME, mimetype=j)
            service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
    if FILE_EXTENSION == 'doc':
        for i, j in zip(FILE_NAME, MINME_TYPE[1]):
            file_metadata = {
                'name': FILE_NAME,
                'parents': [FOLDERS_ID]
            }
            media = MediaFileUpload(
                'line-bot-tutorial-master\static/' + FILE_NAME, mimetype=j)
            service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
    if FILE_EXTENSION == 'docx':
        for i, j in zip(FILE_NAME, MINME_TYPE[2]):
            file_metadata = {
                'name': FILE_NAME,
                'parents': [FOLDERS_ID]
            }
            media = MediaFileUpload(
                'line-bot-tutorial-master\static/' + FILE_NAME, mimetype=j)
            service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent)
def handle_message(event):
    if event.message.type == "text":
        FOUND_FILE = ''
        FOLDERS_NAME = np.array([])
        FOLDERS_NAME = np.append(FOLDERS_NAME, event.message.text.split())
        FOLDERS_NAME = (event.message.text).split()
        page_token = None
        if FOLDERS_NAME[0] == 'create' or FOLDERS_NAME[0] == 'Create' or FOLDERS_NAME[0] == '建立':
            FOLDERS_NAME = np.delete(FOLDERS_NAME, 0)
            for i in FOLDERS_NAME:
                file_metadata = {
                    'name': i,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                service.files().create(body=file_metadata).execute()
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Finished'))
        if FOLDERS_NAME[0] == 'search' or FOLDERS_NAME[0] == 'Search' or FOLDERS_NAME[0] == '搜尋':
            if FOLDERS_NAME[1] == 'image' or FOLDERS_NAME[1] == 'Image' or FOLDERS_NAME[1] == '照片':
                responses = service.files().list(
                    q="mimeType='image/jpeg'",
                    spaces='drive', fields='nextPageToken,files(id, name)',
                    pageToken=page_token).execute()
                for file in responses.get('files', []):
                    FOUND_FILE += str('Found file: '+file.get('name')+'\n')
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text=FOUND_FILE))
                page_token = responses.get('nextPageToken', None)
                if page_token is None:
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text='nothing'))
    if event.message.type == 'image':
        IMG_NAME = ''.join(random.choice(
            string.ascii_letters + string.digits) for x in range(4)).upper()+'.jpg'
        IMG_CONTENT = line_bot_api.get_message_content(event.message.id)
        with open('line-bot-tutorial-master\static/'+IMG_NAME, 'wb') as fd:
            for chunk in IMG_CONTENT.iter_content():
                fd.write(chunk)
            FOLDERS_ID = '1YzuAIUYjXh2M14-59q6ZpgtU-BNXKeo5'
            MINME_TYPE = ['image/jpeg']
            for i, j in zip(IMG_NAME, MINME_TYPE):
                file_metadata = {
                    'name': IMG_NAME,
                    'parents': [FOLDERS_ID]
                }
                media = MediaFileUpload(
                    'line-bot-tutorial-master\static/' + IMG_NAME, mimetype=j)
                service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
    if event.message.type == 'file':
        FILE_JSON = json.loads(str(event.message))
        FILE_NAME = FILE_JSON['fileName']
        FILE_CONTENT = line_bot_api.get_message_content(event.message.id)
        FILE_EXTENSION = FILE_NAME[FILE_NAME.index('.')+1:]
        with open('line-bot-tutorial-master\static/'+FILE_NAME, 'wb') as fd:
            for chunk in FILE_CONTENT.iter_content():
                fd.write(chunk)
            FILE_EXT(FILE_NAME, FILE_EXTENSION)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
