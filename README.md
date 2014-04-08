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

Create the directory /etc/jenkins-gong and copy the file jenkins_gong/config/config.ini into it.
You will probably want to edit the file afterwards and change the url or the extension

Dialplan
--------

Place the following dialplan in /etc/asterisk/xivo-extrafeatures.conf

    [gong]
    exten = s,1,NoOp()
    same  =   n,Answer()
    same  =   n,Hangup()

Cronjob
-------

Create a cronjob file at /etc/cron.d/jenkins-gong with the following line:

    * * * * 1-5 root   /usr/local/bin/jenkins_gong
