# xmpp_monitoring

server monitoring using xmpp

my xmpp server of choice is prosody, running on a raspberry pi

cmdline to start checking host : ./client-main.py -q -j <xmppaccount> -p <password> -r <chatroom_name> -n <xmppaccount_nickname>
cmdline to start client host : ./server-main.py -q -j <xmppaccount>  -p <password> -r <chatroom_name> -n rpi -m true

when a host fails or a checked process isn't running a message is sent to a monitoring account.
The monitoring account is an account that I use on my phone, using the Android Freelab messaging account

Service and host state is stored in a MySQL database, running again on the rpi
