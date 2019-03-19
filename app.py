from __future__ import unicode_literals

import errno, os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URITemplateAction,
    PostbackTemplateAction, DatetimePickerTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

import database
import json 
import datetime
import re
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# get variables from your environment variable
channel_secret = os.environ.get('LINE_CHANNEL_SECRET', None)
channel_access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', None)
admin_id = os.environ.get('ADMIN_ID', None)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

def parse_schedule(content):
    schedule = ""
    try:
        for key in content:
            course_name = key['course_name']
            session = key['session']
            course_code = key['course_code']
            course_room = key['course_room']
            item = "\nSession {}\n{} - {}\n{}\n---".format(session, course_code, course_name, course_room)
            schedule += item
    except:
        schedule = "\n{}\n---".format(content)
    return schedule

firebase_key = os.environ.get('FIREBASE_KEY', None)
database_url = os.environ.get('FIREBASE_DB_URL', None)

cred = credentials.Certificate(json.loads(firebase_key))
dbfb = firebase_admin.initialize_app(cred, {
    'databaseURL': database_url
})

def add_groupwhitelist(groupId):
    global dbfb
    ref = db.reference('/whitelist_groups', dbfb)
    group = ref.get()
    if group == None:
        group = []
    ref.child(str(len(group))).set(str(groupId))
    message = "Group {} has been whitelisted.".format(str(groupId))
    return message

def check_permission(groupId):
    global dbfb
    ref = db.reference('/whitelist_groups', dbfb)
    group = ref.get()
    if groupId in group:
        access = True
    else:
        access = False
    return access

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    if event.source.type == 'user':
        if event.source.user_id != admin_id:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Sorry, this is private bot."))
        else:
            searchText = re.search(r'\/([A-Za-z].*) ([A-Za-z0-9].*)', text, re.I)
            command = str(searchText.group(1))
            if command == 'add':
                groupId = str(searchText.group(2))
                content = add_groupwhitelist(groupId)
                line_bot_api.reply_message(
                    event.reply_token, TextMessage(text=content))
    else:
        command = re.search(r'\/([\w]+)', text, re.I).group(1).lower()
        argument = re.search(r'\/(?:[\w]+)\s([\w\d]+)', text, re.I)
    
        if command == 'bye':
            if isinstance(event.source, SourceGroup):
                line_bot_api.reply_message(
                    event.reply_token, TextMessage(text='Leaving group'))
                line_bot_api.leave_group(event.source.group_id)
            elif isinstance(event.source, SourceRoom):
                line_bot_api.reply_message(
                    event.reply_token, TextMessage(text='Leaving group'))
                line_bot_api.leave_room(event.source.room_id)
            else:
                line_bot_api.reply_message(
                    event.reply_token, TextMessage(text="Bot can't leave from 1:1 chat"))

        if command == 'get':
            profile = line_bot_api.get_group_member_profile(event.source.group_id, event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, TextMessage(text="Hello {}".format(profile.display_name)))
        if command == 'malamute':
            url = "https://dog.ceo/api/breed/Malamute/images/random"
            resp = requests.get(url=url)
            line_bot_api.reply_message(
                event.reply_token, TextMessage(text="{}".format(resp)))
            
            
        if command == 'today' or 'tomorrow' or 'yesterday':
            kelas = str(argument.group(1).lower())
            qa = len(kelas)
            if qa != 1:
                message = "Maaf, input kelas tidak valid."
                line_bot_api.reply_message(
                    event.reply_token, TextMessage(text=message)
                )
            else:
                query = "database.{}_schedule('{}')".format(command, kelas)
                print(query)
                content = exec(query)
                print(content)
                data = parse_schedule(content)
                line_bot_api.reply_message(
                    event.reply_token, TextMessage(
                        text="[{} {}]\n---{}".format(command.upper(), kelas.upper(), data)
                        ))

        else:
            None

@handler.add(JoinEvent)
def handle_join(event):
    if event.source.type is 'group':
        if check_permission(event.source.group_id):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='Thank you for inviting me to this ' + event.source.type))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='Joined unknown group, this incident will be reported.'))
            line_bot_api.push_message(admin_id, TextSendMessage(text='[WARNING] Group was invited to unknown group: ' + event.source.group_id))
            line_bot_api.leave_group(event.source.group_id)
    else:
        line_bot_api.leave_room(event.source.room_id)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
