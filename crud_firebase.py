import os
import json 
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate(json.loads(os.environ['FIREBASE_KEY']))
app = firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ['FIREBASE_DB_URL']
})

def add_groupwhitelist(groupId):
    global app
    ref = db.reference('/whitelist_groups', app)
    group = ref.get()
    if group == None:
        group = []
    ref.child(str(len(group))).set(str(groupId))
    message = "Group {} has been whitelisted.".format(str(groupId))
    return message

def check_permission(groupId):
    global app
    ref = db.reference('/whitelist_groups', app)
    group = ref.get()
    if groupId in group:
        access = True
    else:
        access = False
    return access