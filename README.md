# xmpp_monitoring

server monitoring using xmpp, written in Python3 and based on the sleekxmpp library

my xmpp server of choice is prosody, running on a raspberry pi

cmdline to start checking host : ./client-main.py -q -j <xmppaccount> -p <password> -r <chatroom_name> -n <xmppaccount_nickname>
cmdline to start client host : ./server-main.py -q -j <xmppaccount>  -p <password> -r <chatroom_name> -n rpi -m true

when a host fails or a checked process isn't running a message is sent to a monitoring account.
The monitoring account is an account that I use on my phone, using the Android Freelab messaging account

Service and host state is stored in a MySQL database, running again on the rpi but could be anything

Hosts and processes are checked in 1 of 2 ways:

Host Monitoring

Hosts that capable of running the client-main.py code will join a chatroom. Membership of the chat room implies that the host is up. If the client leaves the chatroom (i.e. the script stops running) then an alert is raised
Hosts that are not capable of running the client (or you don't have the necessary rights to make it run) are ping'ed every couple of seconds. If they do not respond in 2 seconds then an alert is raised to show that they are down

Process Monitoring

Processes are monitored every couple of seconds (currently Linux only), by running the "ps aux" command and grep'ing the output to check that a particular process is runnnig. If the process isn't found an alert is raised

Future plans

 - A web page to show current status
 - the ability to run arbitary scripts and process the result to check things like CPU/Memory/HDD use


