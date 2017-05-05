#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import getpass
import sleekxmpp
import json
import uuid
import time
import subprocess
import os
from optparse import OptionParser

dir_path = os.path.dirname(os.path.realpath(__file__))
module_path = os.path.join(dir_path,'modules')

sys.path.append(module_path)
from database import MySQLdb
from load_variables import load_variables
from ping_host import ping_host



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
		self.external_vars = {}
		self.task_queue_file = ""
		self.monitoring_account = ""
		self.host_history = {}

		self.add_event_handler("session_start", self.start)
		self.add_event_handler("groupchat_message", self.muc_message)
		self.add_event_handler("message", self.message)
		self.add_event_handler("muc::%s::got_online" % self.room,self.muc_online)
		self.add_event_handler("muc::%s::got_offline" % self.room,self.muc_offline)
		self.add_event_handler("got_offline",self.got_offline)
		self.add_event_handler("got_online",self.got_online)

		self.schedule("auto send message",10,self.auto_message,repeat=True)
	def prepare_db_connection(self):
		#print (self.external_vars)
		self.db = MySQLdb()
		self.db.dbhost = self.external_vars['database_host']
		self.db.dbuser = self.external_vars['database_user']
		self.db.dbpassword = self.external_vars['database_password']
		self.db.db = "Monitoring"
		self.monitoring_account = self.external_vars['monitoring_account']



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
		#print (received_text)
		try:
			received_text_dict=json.loads(str(received_text))            
		except:
			received_text_dict="bad"
		#print (received_text_dict)

	def message(self, msg):
		# we're expecing a dict
		received_text=msg['body']
		#print (received_text)

		try:
			received_text_dict=json.loads(str(received_text)) 
		except:
			print (received_text)
			received_text_dict={}

		if "check_result" in received_text_dict:
			received_text_dict_check_result = received_text_dict['check_result']
			process_result = received_text_dict_check_result['process_result']
			check_id = received_text_dict_check_result['check_id']
			sending_host = msg['from']

			# get check info from Process_tmp and then delete entry
			sqlquery = "select REQUESTTIME,PROCESSID from Process_tmp where UID = '{check_id}';".format(**locals())
			result = self.db.Query(sqlquery)			
			db_requesttime = result[0]['REQUESTTIME']
			db_processid = result[0]['PROCESSID']

			sqldelete = "DELETE from Process_tmp where UID = '{check_id}';".format(**locals())
			result = self.db.Delete(sqldelete)

			# now look to see if there's an entry in the "current state" table for this processid
			# if there is, compare the result. if the result is the same do nothing
			#	if the result is different update the db and alert the monitor account
			# if there is no entry in the table, add one and store the current state

			sqlquery = "select count(*) from Process_State where PROCESSID = '{db_processid}';".format(**locals())
			result = self.db.Query(sqlquery)	
			process_count=int(result[0]['count(*)'])
			#print (sqlquery,result,process_count,process_count.__class__)

			if process_count == 0:
				sqlinsert = """INSERT into Process_State (PROCESSID,CURRENTSTATE,LASTSTATE,LASTSTATECHANGE) 
					VALUES ('{db_processid}','{process_result}','0',now());""".format(**locals())
				self.db.Insert(sqlinsert)
			if process_count >=1:
				sqlquery = "select CURRENTSTATE from Process_State where PROCESSID = '{db_processid}';".format(**locals())
				result = self.db.Query(sqlquery)
				db_currentstate = result[0]['CURRENTSTATE']
				if int(db_currentstate) != int(process_result):
					# get process name
					sqlquery = "select PROCESSNAME from Processes where ID='{db_processid}';".format(**locals())
					result = self.db.Query(sqlquery)
					process_name = result[0]['PROCESSNAME']
					sqlupdate = """update Process_State 
						set CURRENTSTATE='{process_result}', LASTSTATE='{db_currentstate}', LASTSTATECHANGE=now()
						where PROCESSID='{db_processid}'""".format(**locals())
					self.db.Update(sqlupdate)
					message = """Service {process_name} on host {sending_host} has changed state, 
					from {db_currentstate} to {process_result}""".format(**locals())
					self.send_message(mto=self.monitoring_account,mbody=message,mtype='normal')

		if "check_request" in received_text_dict:
			received_text_dict_check_request = received_text_dict['check_request']
			msg_time = received_text_dict_check_request['msg_time']
			now = time.time()
			delta = now - int(msg_time)
			if delta < 15: 
				if "check_process" in received_text_dict_check_request:
					process = received_text_dict_check_request['check_process']
					process_result = self.check_process(process)
					return_msg_dict = {"check_result:":{"check_id":received_text_dict_check_request['check_id'],
										"process_result": process_result }}
					msg.reply(json.dumps(return_msg_dict)).send()
			#except:
			#	received_text_dict="bad"
		
		#self.send_message(mto=self.monitoring_account,mbody=str(received_text_dict),mtype='chat')


	def muc_online(self, presence):
		# add host to list of online hosts
		print ("MUC online: %s " % presence['muc']['nick'])
		self.presence = presence
		if mod:
			with open(self.task_queue_file) as json_data:
				d = json.load(json_data)
			if presence['muc']['nick'] in d:
				message = "%s is MUC_ONLINE" % presence['muc']['nick']
				self.send_message(mto=self.monitoring_account,mbody=message,mtype='chat')

	def muc_offline(self,presence):
		# mark host as offline
		print ("MUC offline: %s" % presence['muc']['nick'])
		self.presence = presence
		if mod:
			with open(self.task_queue_file) as json_data:
				d = json.load(json_data)
			if presence['muc']['nick'] in d:
				message = "%s is MUC_OFFLINE" % presence['muc']['nick']
				self.send_message(mto=self.monitoring_account,mbody=message,mtype='chat')

	def got_offline(self,presence):
		print ("got_offline: %s %s" % (presence['muc']['nick'],presence['muc']['role']) )
		self.presence = presence
		if mod:
			message = "%s is OFFLINE" % presence['muc']['nick']
			self.send_message(mto=self.monitoring_account,mbody=message,mtype='chat')
			host_name = presence['muc']['nick']
			task_queue_file = self.task_queue_file
			with open(task_queue_file) as json_data:
				d = json.load(json_data)
			for key in d:
				if "xmpp_nickname" in d[key]:
					xmpp_nickname = d[key]['xmpp_nickname']
					if host_name == xmpp_nickname.split('@')[0]:
						if key not in self.host_history:
							self.host_history[key]={'alert_after_failures':1,
									'recent_history': [False],
									'alert_open' : False
									}
						else:
								self.host_history[key]['recent_history'].append(False)
						self.host_status(host_name ,False)

	def got_online(self,presence):
		print ("got_online: %s %s" % (presence['muc']['nick'],presence['muc']['role'])  ) 
		self.presence = presence  
		if mod:
			message = "%s is ONLINE" % presence['muc']['nick']
			self.send_message(mto=self.monitoring_account,mbody=message,mtype='chat')
			host_name = presence['muc']['nick']
			# check to see if this host is in the task_queue.ini file
			task_queue_file = self.task_queue_file
			with open(task_queue_file) as json_data:
				d = json.load(json_data)
			for key in d:
				if "xmpp_nickname" in d[key]:
					xmpp_nickname = d[key]['xmpp_nickname']
					if host_name == xmpp_nickname.split('@')[0]:
						if key not in self.host_history:
							self.host_history[key]={'alert_after_failures': 1,
									'recent_history': [True],
									'alert_open' : False
									}
						else:
							self.host_history[key]['recent_history'].append(True)
							if len(self.host_history[key]['recent_history']) >= 100:
                                                        	self.host_history[key]['recent_history'].pop(0)

						self.host_status(host_name ,True)


	def auto_message(self):
		# this is the process that checks processes etc
		if mod:
			task_queue_file = self.task_queue_file
			with open(task_queue_file) as json_data:
				d = json.load(json_data)
			for key in d:
				#print ("%s %s" % (key,d[key]))
				#print ("Host Alias: {host}".format(host=key))
				if "process_checks" in d[key]:
					#print ("Process checks:")
					for pc in d[key]['process_checks']:
						check_id = str(uuid.uuid4())
						send_check_dict = {"check_request":{"check_process":pc,
											"msg_time": time.time(),
											"check_id": check_id}}
						message = json.dumps(send_check_dict)
						#print (message)
						if 'xmpp_nickname' in d[key]:
							self.send_message(mto=d[key]['xmpp_nickname'],
								mbody=message,
								mtype='chat')

							# get process ID
							sqlquery = "select ID from Processes where PROCESSNAME='{pc}' limit 1;".format(**locals())
							result = self.db.Query(sqlquery)
							if len(result) is 0:
								sqlinsert = "INSERT into Processes (PROCESSNAME) VALUES ('{pc}');".format(**locals())
								self.db.Insert(sqlinsert)
								sqlquery = "select ID from Processes where PROCESSNAME='{pc}' limit 1;".format(**locals())
								result = self.db.Query(sqlquery)
								#print (result)
								process_id = result[0]['ID']
							else:
								process_id = result[0]['ID']

							# make entry in database to record fact that a check has been made
							sqlinsert = """INSERT into Process_tmp (UID,REQUESTTIME,PROCESSID)
											 VALUES ('{check_id}',now(),'{process_id}');""".format(**locals())
							self.db.Insert(sqlinsert)
				if 'ip_address' in d[key]:
					host_online = ping_host(d[key]['ip_address'])
					#print ("host_status of {host}: {host_status}".format(
					#	host = d[key]['ip_address'], host_status = host_online ) )
					# update data base. check to see if host is in hosts table
					#  if it isn't add it and then get the ID
					#  if it is
					if key not in self.host_history:
						self.host_history[key]={'alert_after_failures': int(d[key]['alert_after_failures']),
												'recent_history': [host_online],
												'alert_open' : False
												}
					else:
						self.host_history[key]['recent_history'].append(host_online)
						if len(self.host_history[key]['recent_history']) >= 100: 
							self.host_history[key]['recent_history'].pop(0)

					self.host_status(key,host_online)

	def host_status(self,host_name,host_online):
		#print (self.host_history[host_name])
		sqlquery = "select ID from Hosts where HOSTNAME = '{host_name}';".format(**locals())
		result = self.db.Query(sqlquery)
		if len(result) is 0:
			sqlinsert="insert into Hosts (HOSTNAME) values ('{host_name}');".format(**locals())
			self.db.Insert(sqlinsert)
			sqlquery = "select ID from Hosts where HOSTNAME = '{host_name}';".format(**locals())
			result = self.db.Query(sqlquery)
			host_id = result[0]['ID']
			host_in_db = False
		else:
			host_id = result[0]['ID']
			host_in_db = True

		if host_online:
			CURRENTSTATE = 0
			if not host_in_db:
				sqlupdate = "update Hosts set FIRSTSEEN=now() and LASTSEEN=now() where ID='%s';" % host_id
				self.db.Update(sqlupdate)
				sqlinsert = """insert into Host_State (HOSTID,CURRENTSTATE,LASTSTATE,LASTSTATECHANGE)
						VALUES ('{host_id}','{CURRENTSTATE}','0',now() )""".format(**locals())
				print (sqlinsert)
				self.db.Insert(sqlinsert)
			else:
				sqlupdate = "update Hosts set LASTSEEN=now() where ID='%s';" % host_id
				self.db.Update(sqlupdate)

				# check to see if the current state has changed
				sqlquery = "select CURRENTSTATE from Host_State where HOSTID='{host_id}';".format(**locals())
				result = self.db.Query(sqlquery)
				if len(result) >= 1:
					db_currentstate = result[0]['CURRENTSTATE']
					if db_currentstate != CURRENTSTATE:
						sqlupdate = """update Host_State set CURRENTSTATE='{CURRENTSTATE}',LASTSTATE='{db_currentstate}',LASTSTATECHANGE=now()
						 where HOSTID='{host_id}'""".format(**locals())
						self.db.Update(sqlupdate)
				else:
					sqlinsert = """insert into Host_State (HOSTID,CURRENTSTATE,LASTSTATE,LASTSTATECHANGE) 
								values ('{host_id}','{CURRENTSTATE}','{CURRENTSTATE}',now());""".format(**locals())
					print (sqlinsert)
					self.db.Insert(sqlinsert)
				### also send an alert to the monitoring account here
				if 'alert_after_failures' not in self.host_history[host_name]: failures_before_alert = 1
				else: failures_before_alert = self.host_history[host_name]['alert_after_failures']

				if len(set(self.host_history[host_name]['recent_history'][ - failures_before_alert:])) == 1: # recent status checks have all had the same result.
					if self.host_history[host_name]['alert_open'] == True:
						message = "Host: %s is now ONLINE" % (host_name)
						self.send_message(mto=self.monitoring_account,mbody=message,mtype='chat')
						self.host_history[host_name]['alert_open'] = False
		else:
			CURRENTSTATE = 1
			if not host_in_db:
				sqlupdate = "update Hosts set FIRSTSEEN='0000-00-00 00:00:00' and LASTSEEN='0000-00-00 00:00:00' where ID='%s';" % host_id
				self.db.Update(sqlupdate)
				sqlinsert = """insert into Host_State (HOSTID,CURRENTSTATE,LASTSTATE,LASTSTATECHANGE)
						VALUES ('{host_id}','{CURRENTSTATE}','0',now() )""".format(**locals())
				self.db.Insert(sqlinsert)
			else:
				# check to see if the current state has changed
				sqlquery = "select CURRENTSTATE from Host_State where HOSTID='{host_id}';".format(**locals())
				result = self.db.Query(sqlquery)
				if len(result) >= 1:
					db_currentstate = result[0]['CURRENTSTATE']
					if db_currentstate != CURRENTSTATE:
						sqlupdate = """update Host_State set CURRENTSTATE='{CURRENTSTATE}',LASTSTATE='{db_currentstate}',LASTSTATECHANGE=now()
						 where HOSTID='{host_id}'""".format(**locals())
						self.db.Update(sqlupdate)

				
				### also send an alert to the monitoring account here
				if 'alert_after_failures' not in self.host_history[host_name]: failures_before_alert = 1
				else: failures_before_alert = self.host_history[host_name]['alert_after_failures']
				
				#print (host_name,failures_before_alert,self.host_history[host_name]['recent_history'])
				#print (self.host_history[host_name]['alert_after_failures'])
				#print (self.host_history[host_name]['recent_history'][-failures_before_alert:]) 

				if len(set(self.host_history[host_name]['recent_history'][ - failures_before_alert:])) == 1: # recent status checks have all had the same result.
					if self.host_history[host_name]['alert_open'] == False:
						message = "Host: %s has gone OFFLINE" % (host_name)
						self.send_message(mto=self.monitoring_account,mbody=message,mtype='chat')
						self.host_history[host_name]['alert_open'] = True



if __name__ == '__main__':

    
    variables_file = os.path.join(dir_path,"etc/monitoring.ini")
    task_queue_file = os.path.join(dir_path,"etc/task_queue.ini")
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

    xmpp.external_vars = load_variables(variables_file)
    xmpp.task_queue_file = task_queue_file
    xmpp.prepare_db_connection()

    xmpp_server_address = xmpp.external_vars['xmpp_server'].split(':')[0]
    xmpp_server_port = xmpp.external_vars['xmpp_server'].split(':')[1]

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect((xmpp_server_address,xmpp_server_port)):
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

