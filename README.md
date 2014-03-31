XiVO Gong
=========

Plays a "gong" on a loud ringer when a new job fails on jenkins.

Requirements
===========

 * A SIP Loud Ringer, like the Algo 8180
 * Jenkins server
 * XiVO server

Dependencies
============

 * python (2.7, 3.x)
 * requests

install requests with "pip install requests"

Configuration
=============

failed_jobs.py
--------------

Edit the python script and put the address of your jenkins server in the URL
variable like so:

    URL = "http://jenkins.server.com/api/json"

Dialplan
--------

Place the following dialplan in /etc/asterisk/xivo-extrafeatures.conf

    [gong]
    exten = s,1,NoOp()
    same  =   n,Answer()
    same  =   n,Hangup()

Cronjob
-------

Edit the script jenkins-gong.sh and put the extension of the ringer in the EXTENSION
variable like so:

    EXTENSION='1000@default'

Then create a cronjob file at /etc/cron.d/jenkins-gong with the following line:

    * * * * 1-5 root   /usr/local/bin/jenkins-gong.sh
