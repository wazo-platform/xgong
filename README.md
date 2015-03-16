XiVO Gong
=========

Plays audio messages on a loud ringer. Used to alert the XiVO team when jobs on
jenkins have failed. The project is divided into 2 parts:

 * xgong

    Micro HTTP service used for playing audio messages on the ringer. Audio
    files can be uploaded and scheduled to be played immediately or in the
    future.

 * xgong-jenkins

    Client app that will periodically check a jenkins server for failed jobs
    and send notifications to the xgong HTTP server.

Server API
==========

By default, the server listens on port 9600

 * GET /messages

    Return a list of all audio messages that are scheduled to be played on the ringer

 * POST /messages/add

    Add a new file to the schedule. File must be uploaded using a multipart form.

    Parameters:

    * audio: The audio file. Required.
    * extension: Call this extension and play the message. If no extension is sent, use default.
    * start: Timestamp for when the message should be played. If no timestamp
      is sent, the file will be played immediately. Timestamps must be formatted as
      "{YEAR}-{MONTH}-{DAY}T{HOUR}:{MINUTE}:{SECOND}" (without the braces).

 * POST /messages/tts/add

    Generate a message using a Text-To-Speech engine.

    Parameters:

    * text: The text to use for the message
    * extension: Call this extension and play the message. If no extension is sent, use default.
    * start: Timestamp for when the message should be played. If no timestamp
      is sent, the file will be played immediately. Timestamps must be formatted as
      "{YEAR}-{MONTH}-{DAY}T{HOUR}:{MINUTE}:{SECOND}" (without the braces).

 * DELETE /messages/{id}

    Delete a message. Only messages that have not been played yet can be deleted


Requirements
============

 * A SIP Loud Ringer, like the Algo 8180
 * Jenkins server
 * XiVO server

Dependencies
============

 * python (2.7)
 * requests
 * uwsgi
 * sox

On debian, these dependencies can be installed like so :

    sudo apt-get install python2.7 python-requests uwsgi sox libsox-fmt-mp3


Build dependencies
==================

To build on debian, you will need essential building tools and
[dh-virtualenv](http://dh-virtualenv.readthedocs.org). Most tools needed (except
dh-virtualenv) can be installed like so:

    sudo apt-get install build-essential dpkg-dev debhelper python-all python-setuptools

After that, you can build both packages

    #build xgong server
    cd xgong/xgong
    dpkg-buildpackage -us -uc

    #build xgong jenkins client
    cd xgong/xgong-jenkins
    dpkg-buildpackage -us -uc


Configuration
=============

Under debian, config files will automatically be installed under /etc/xgong.
You will probably want to change the following options:

 * extension (config.ini)

    Extension used to dial the loud ringer

 * url (jenkins.ini)

    URL of the jenkins server to check
