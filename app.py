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
import datetime

app = Flask(__name__)

# get variables from your environment variable
channel_secret = os.environ.get('LINE_CHANNEL_SECRET', None)
channel_access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', None)
allowed_groupid = os.environ.get('ALLOWED_GROUPID', None)
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
            lecturer_name = key['lecturer_name']
            item = "\nSession {}\n{} - {}\n{}\n{}\n---".format(session, course_code, course_name, lecturer_name, course_room)
            schedule += item
    except:
        schedule = "\n{}\n---".format(content)
    return schedule    

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
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Sorry, this is private bot."))
    else:
        if text == '/bye':
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
        if '/today' in text:
                KELAS = text.split(' ')[1]
                content = database.today_schedule(KELAS)
                schedule = parse_schedule(content)
                line_bot_api.reply_message(
                    event.reply_token, TextMessage(text="[TODAY {}]\n---{}".format(KELAS.upper(), schedule)))
        if '/tomorrow' in text:
                KELAS = text.split(' ')[1]
                content = database.today_schedule(KELAS)
                schedule = parse_schedule(content)
                line_bot_api.reply_message(
                    event.reply_token, TextMessage(text="[TOMORROW {}]\n---{}".format(KELAS.upper(), schedule)))
        if '/get' in text:
            if isinstance(event.source, SourceUser):
                profile = line_bot_api.get_profile(event.source.user_id)
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='Display name: ' + profile.display_name),
                        TextSendMessage(text='UUID: ' + profile.user_id)]
                        )
            else:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))

@handler.add(JoinEvent)
def handle_join(event):
    if event.source.type is 'group':
        if event.source.group_id == allowed_groupid:
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
