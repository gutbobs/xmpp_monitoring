#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp
import json
import uuid
import time
import subprocess

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class MUCBot(sleekxmpp.ClientXMPP):
	def __init__(self, jid, password, room, nick, mod):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)

		self.room = room
		self.nick = nick
		self.count = 0

		self.add_event_handler("session_start", self.start)
		self.add_event_handler("groupchat_message", self.muc_message)
		self.add_event_handler("message", self.message)
		self.add_event_handler("muc::%s::got_online" % self.room,self.muc_online)
		self.add_event_handler("muc::%s::got_offline" % self.room,self.muc_offline)
		self.add_event_handler("got_offline",self.got_offline)
		self.add_event_handler("got_online",self.got_online)

		self.schedule("auto send message",10,self.auto_message,repeat=True)


	def start(self, event):
		self.get_roster()
		self.send_presence()
		self.plugin['xep_0045'].joinMUC(self.room,
			self.nick,
			# If a room password is needed, use:
			# password=the_room_password,
			wait=True)

	def muc_message(self, msg):
		# we're expecing a dict
		received_text=msg['body']
		print (received_text)
		try:
			received_text_dict=json.loads(str(received_text))            
		except:
			received_text_dict="bad"
		print (received_text_dict)

	def check_process(self,process):
		cmd = "ps aux | grep {process} | grep -v grep".format(**locals())
		p = subprocess.Popen(cmd,shell=True, stdout = subprocess.PIPE)
		result = p.wait()
		print ("{cmd}, {result}".format(**locals()))
		return result

	def message(self, msg):
		# we're expecing a dict
		received_text=msg['body']
		print (received_text)

		received_text_dict=json.loads(str(received_text)) 
		if "check_request" in received_text_dict:
			received_text_dict_check_request = received_text_dict['check_request']
			msg_time = received_text_dict_check_request['msg_time']
			now = time.time()
			delta = now - int(msg_time)
			if delta < 15: 
				if "check_process" in received_text_dict_check_request:
					process = received_text_dict_check_request['check_process']
					process_result = self.check_process(process)
					return_msg_dict = {"check_result":{"check_id":received_text_dict_check_request['check_id'],
										"process_result": process_result }}
					msg.reply(json.dumps(return_msg_dict)).send()
			#except:
			#	received_text_dict="bad"
		
		#self.send_message(mto="monitor@hill.lan",mbody=str(received_text_dict),mtype='chat')


	def muc_online(self, presence):
		# add host to list of online hosts
		print ("MUC online: %s " % presence['muc']['nick'])
		self.presence = presence
		if mod:
			message = "%s is MUC_ONLINE" % presence['muc']['nick']
			self.send_message(mto="monitor@hill.lan",mbody=message,mtype='chat')

	def muc_offline(self,presence):
		# mark host as offline
		print ("MUC offline: %s" % presence['muc']['nick'])
		self.presence = presence
		if mod:
			message = "%s is MUC_OFFLINE" % presence['muc']['nick']
			self.send_message(mto="monitor@hill.lan",mbody=message,mtype='chat')

	def got_offline(self,presence):
		print ("got_offline: %s %s" % (presence['muc']['nick'],presence['muc']['role']) )
		self.presence = presence
		if mod:
			message = "%s is OFFLINE" % presence['muc']['nick']
			self.send_message(mto="monitor@hill.lan",mbody=message,mtype='chat')

	def got_online(self,presence):
		print ("got_online: %s %s" % (presence['muc']['nick'],presence['muc']['role'])  ) 
		self.presence = presence  
		if mod:
			message = "%s is ONLINE" % presence['muc']['nick']
			self.send_message(mto="monitor@hill.lan",mbody=message,mtype='chat')

	def auto_message(self):
		# this is the process that checks processes etc
		if mod:
			task_queue_file = "task_queue.ini"
			with open(task_queue_file) as json_data:
				d = json.load(json_data)
			for key in d:
				#print ("%s %s" % (key,d[key]))
				print ("Host Alias: {host}".format(host=key))
				if "process_checks" in d[key]:
					print ("Process checks:")
					for pc in d[key]['process_checks']:
						check_id = str(uuid.uuid4())
						send_check_dict = {"check_request":{"check_process":pc,
											"msg_time": time.time(),
											"check_id": check_id}}
						message = json.dumps(send_check_dict)
						print (message)
						self.send_message(mto=d[key]['xmpp_nickname'],
							mbody=message,
							mtype='chat')





if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-r", "--room", dest="room",
                    help="MUC room to join")
    optp.add_option("-n", "--nick", dest="nick",
                    help="MUC nickname")
    optp.add_option("-m", "--mod", dest="mod",
                help="user is moderator")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    if opts.room is None:
        opts.room = raw_input("MUC room: ")
    if opts.nick is None:
        opts.nick = raw_input("MUC nickname: ")
    if opts.mod is None: 
    	mod = False
    else: 
        mod = True

    # Setup the MUCBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = MUCBot(opts.jid, opts.password, opts.room, opts.nick,mod)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0045') # Multi-User Chat
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect(('192.168.1.21',5222)):
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(threaded=False)
        print("Done")
    else:
        print("Unable to connect.")

