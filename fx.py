#!/usr/bin/python3.7
# Download the helper library from https://www.twilio.com/docs/python/install

import sqlite3
from twilio.rest import Client
from time import sleep
from config import *


create_table = '''CREATE TABLE IF NOT EXISTS reclogs (id INTEGER PRIMARY KEY AUTOINCREMENT, recid INTERGER)'''

client = Client(account_sid, auth_token)

recordings = client.recordings.list()
messages = client.messages.list(limit=20, from_=phone_cell)

conn = sqlite3.connect('recordlist.db')
cursor = conn.cursor()
cursor.execute(create_table)

#client.messages('MMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX').delete() 

to_delete_recordings = set()

for message in messages:

	if 'delete' in message.body.lower():
		dellist = message.body.lower().split(' ')
		dellist.pop(0)
		# print(dellist)
		for e in dellist:
			# print(e)
			try:
				int(e)
			except Exception as asdf:
				pass
			else:
				to_delete_recordings.add(e)
			
			# if 'all' in e:
			# 	to_delete_recordings.add(e)
			# # print(to_delete_recordings)
		message.delete()

for record in recordings:
	s = record.sid

	recid = cursor.execute('select * from reclogs where recid like ?', (s,)).fetchone()
	if recid:
		pass
	else:
		cursor.execute("insert into reclogs(recid) values (?)", ((s,)))
		conn.commit()
		recid = cursor.execute(
			'select * from reclogs where recid like ?', (s,)).fetchone()
		
		c = client.calls(record.call_sid).fetch()
		link = 'https://api.twilio.com/2010-04-01/Accounts/{}/Recordings/{}.mp3'.format(account_sid, s)
		body = 'vm from: {} id: {} link: {}'.format(c.from_formatted, recid[0], link)
		m = client.messages.create(body=body, to=phone_cell, from_=phone_home)
	conn.commit()

for to_ in to_delete_recordings:
	del_rec = cursor.execute(
		'select recid from reclogs where id like ?', (to_)).fetchone()
	try:
		client.recordings(del_rec[0]).delete()
	except Exception as whocares:
		pass
	cursor.execute('delete from reclogs where id = ?', (to_,))
	conn.commit()

conn.commit()
conn.close()

