import uuid
import os
import pwd
import grp
import audio
import shutil
import tempfile
import json

from datetime import datetime, timedelta
from bottle import run, request, post, get, delete, abort
from ConfigParser import ConfigParser

config = ConfigParser()
config.read(['/etc/xgong/config.ini'])

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


@get('/messages')
def list_messages():
    messages = tuple(encode_message(m) for m in all_messages())
    return {'messages': messages}


def encode_message(message):
    return {'id': message['id'],
            'description': message['description'],
            'start': message['start'].strftime(DATETIME_FORMAT)}


def all_messages():
    callfile_dir = config.get('xgong', 'callfiles')

    files = (os.path.join(callfile_dir, f)
             for f in os.listdir(callfile_dir)
             if f.startswith('xgong'))

    return (load_message_file(f) for f in files)


def load_message_file(path):
    start = datetime.fromtimestamp(os.path.getmtime(path))
    with open(path) as f:
        data = f.readline()[2:]
        data = json.loads(data)
        data['start'] = start

    return data


@post('/messages/add')
def add_message():
    if 'audio' not in request.files:
        abort(400, 'missing audio file')

    message = {'description': request.forms.get('description', ''),
               'id': str(uuid.uuid4())}
    if 'start' in request.forms:
        message['start'] = datetime.strptime(request.forms['start'],
                                             DATETIME_FORMAT)

    generate_audio_file(request.files['audio'], message['id'])
    add_callfile(message)
    adjust_schedules()


def add_callfile(message):
    extension = config.get('xgong', 'extension')
    filepath = audio_path(message['id'], '')
    data = encode_for_callfile(message)
    max_retries = config.get('xgong', 'max_retries')
    retry_time = config.get('xgong', 'retry_time')

    lines = ['# {}'.format(data),
             'Channel: Local/{}'.format(extension),
             'Context: xgong',
             'Extension: s',
             'MaxRetries: {}'.format(max_retries),
             'RetryTime: {}'.format(retry_time),
             'Setvar: AUDIO_FILE={}'.format(filepath)]

    callfile = os.path.join(config.get('xgong', 'tmp_callfiles'), message['id'])
    with open(callfile, 'w') as f:
        f.writelines("{}\n".format(l) for l in lines)

    if 'start' in message:
        time = int(message['start'].strftime("%s"))
        os.utime(callfile, (time, time))

    new_path = callfile_path(message['id'])
    shutil.move(callfile, new_path)


def encode_for_callfile(message):
    return json.dumps({'id': message['id'],
                       'description': message['description']})


@delete('/messages/<message_id>')
def delete_message(message_id):
    callfile = callfile_path(message_id)
    audiofile = audio_path(message_id)

    if not all((os.path.exists(callfile), os.path.exists(audiofile))):
        abort(404)

    os.unlink(callfile)
    os.unlink(audiofile)


def generate_audio_file(upload, uid):
    path = audio_path(uid)
    audio.convert_file(upload, path)
    audio.prepend_silence(path, config.get('xgong', 'silence'))


def audio_path(uid, exten='.wav'):
    name = "{}{}".format(uid, exten)
    return os.path.join(config.get('xgong', 'audio'), name)


def callfile_path(uid):
    name = "xgong_{}".format(uid)
    return os.path.join(config.get('xgong', 'callfiles'), name)


def adjust_schedules():
    messages = list(all_messages())
    scheduled = [messages.pop(0)]

    for message in messages:
        last = scheduled[-1]
        end = (last['start'] +
               audio.file_duration(audio_path(last['id'])) +
               timedelta(seconds=1))

        if message['start'] <= end:
            message['start'] = end
        scheduled.append(message)

    for message in scheduled:
        path = callfile_path(message['id'])
        time = int(message['start'].strftime("%s"))
        os.utime(path, (time, time))


def setup():
    audiodir = config.get('xgong', 'audio')
    if not os.path.exists(audiodir):
        os.makedirs(audiodir)


if __name__ == "__main__":
    setup()
    run(host='0.0.0.0', port=8000, debug=True, reloader=True)
