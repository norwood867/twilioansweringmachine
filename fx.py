#!/usr/bin/python3.7
# Download the helper library from https://www.twilio.com/docs/python/install

"""
* This is a simple twilo answering machine. 
"""

import sqlite3
from twilio.rest import Client
from time import sleep
from config import *

to_delete_recordings = set() # to be removed from database

create_table = '''CREATE TABLE IF NOT EXISTS reclogs (id INTEGER PRIMARY KEY AUTOINCREMENT, recid INTERGER)'''

client = Client(account_sid, auth_token) # twilio client setup

messages = client.messages.list(from_=phone_cell) # get messages 

conn = sqlite3.connect('recordlist.db') # automatically creates the database if it doesn't exist
cursor = conn.cursor()
cursor.execute(create_table) # create table if it doesn't exist

def get_from_db_rec():
    # * pull back the complete list of records that messages have been sent about.
    cursor.execute('select * from reclogs')
    d = cursor.fetchall()
    if d:
        a, b = zip(*d)
        return a, b
    return (), ()


#client.messages('MMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX').delete() 

def sendtxt(body):
    # * send message to cellphone
    return client.messages.create(body=body, to=phone_cell, from_=phone_home)


def delete_recording(id):
    # * delete recording on twilio and record in database
    del_rec = cursor.execute(
        'select recid from reclogs where id like ?', (id,)).fetchone()
    try:
        client.recordings(del_rec[0]).delete()
    except Exception:
        # if delete fails because recording is not there, fine
        # if fails for another reason, then the message will get picked up again as a new message
        # so, should be no orphans on twilio
        pass
    cursor.execute('delete from reclogs where id = ?', (id,))
    conn.commit()
    return True
    

for message in messages:
    # * parse message back from cellphone
    # * ignoring messages not starting with del and continue a int
    # * delete immediately
    if message.body.lower().startswith('del'):
        dellist = message.body.lower().split()
        dellist.pop(0)
        for e in dellist:
            try:
                int(e)
            except Exception as asdf:
                pass
            else:
                # 
                delete_recording(e)
        message.delete()
    else:
        # ignoring the other messages for now
        pass


db_rec_id, db_rec_sid = get_from_db_rec() # get db id's and corresponding rec_sids
recordings = client.recordings.list()  # get recordings info
recordings_sids = [e.sid for e in recordings]  # get recordings sids

for record in set(recordings_sids).difference(set(db_rec_sid)):
    # * compare recording on twilio with record of those in database
    # * add new recordings to database list, return id, and send text message to cellphone
    cursor.execute("insert into reclogs(recid) values (?)", ((record,)))
    conn.commit()
    recid = cursor.execute(
            'select * from reclogs where recid like ?', (record,)).fetchone()
    r = recordings[recordings_sids.index(record)]
    c = client.calls(r.call_sid).fetch()
    link = 'https://api.twilio.com/2010-04-01/Accounts/{}/Recordings/{}.mp3'.format(
            account_sid, record)
    body = 'vm from: {} id: {} link: {}'.format(c.from_formatted, recid[0], link)
    m = sendtxt(body)


# * remove records in db that might have been removed from twilio a different way
for record in set(db_rec_sid).difference(set(recordings_sids)):
    cursor.execute('delete from reclogs where recid = ?', (record,))

conn.commit()
conn.close()
