#!/usr/bin/env python3
import subprocess

def ping_host(host):
	cmdline = "ping -c 1 -W 2 %s" % host
	p = subprocess.Popen(cmdline,shell = True, stdout = subprocess.PIPE)
	result = p.wait()
	if result == 0: return True
	else: return False
	