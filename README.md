# XiVO Gong

Plays audio messages on a loud ringer. Used to alert the XiVO team when jobs on
jenkins have failed. The project is divided into 2 parts:

 * xgong

    Micro HTTP service used for playing audio messages on the ringer. Audio
    files can be uploaded and scheduled to be played immediately or in the
    future.

 * xgong-jenkins

    Client app that will periodically check a jenkins server for failed jobs
    and send notifications to the xgong HTTP server.

## Requirements

 * A SIP Loud Ringer, like the Algo 8180
 * Jenkins server
 * XiVO server

## Dependencies

 * bottle
 * python (2.7)
 * requests
 * sox

## Installation

   cat > /etc/apt/sources.list.d/xivo-dev-tools.list << EOF
   deb http://mirror.wazo.community/debian/ xivo-dev-tools main
   EOF
   apt-get update

   apt-get install xgong xgong-jenkins

## Configuration

Under debian, config files will automatically be installed under `/etc/xgong`.
You will probably want to change the following options:

 * extension (config.ini)

    Extension used to dial the loud ringer

 * `apikey` (config.ini)

    Your Voice RSS API key

 * url (jenkins.ini)

    URL of the jenkins server to check

After modifying `/etc/xgong/config.ini`, you must restart `xgong`:

   systemctl restart xgong


## Server API

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


## Build dependencies

Most tools needed can be installed like so:

    sudo apt-get install build-essential dpkg-dev debhelper python-all python-setuptools

After that, you can build both packages

    dpkg-buildpackage -us -uc


## How xgong works

1. Every minute, crond runs `xgong_jenkins`
2. `xgong_jenkins` queries Jenkins to know what jobs have failed
3. `xgong_jenkins` compares the list of failed jobs to the last known list stored in `/tmp/last_failed_jobs.json`
4. If a job failed in the last minute, `xgong_jenkins` asks `xgong` to announce on the loud ringer the names of the failed jobs
5. `xgong` generates a sound file through TTS via VoiceRSS
6. `xgong` gives a callfile to Asterisk
7. Asterisk calls the loud ringer
8. The loud ringer answers
9. Asterisk plays the sound file
