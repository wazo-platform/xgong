import uuid
import os
import audio
import shutil
import tempfile
import json

from datetime import datetime
from bottle import run, request, post, get, delete, abort
from ConfigParser import ConfigParser

config = ConfigParser()
config.read(['/etc/xgong/config.ini'])

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


@get('/messages')
def list_messages():
    return {'messages': all_messages()}


def all_messages():
    callfile_dir = config.get('gong', 'callfiles')

    files = (os.path.join(callfile_dir, f)
             for f in os.listdir(callfile_dir)
             if f.startswith('xgong'))

    return tuple(load_message_file(f) for f in files)


def load_message_file(path):
    start = datetime.fromtimestamp(os.getmtime(path))
    with open(path) as f:
        data = f.readline()[2:]
        data = json.loads(data)
        data['start'] = start

    return start


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


def add_callfile(message):
    extension = config.get('gong', 'extension')
    filepath = audio_path(message['uid'], '')
    data = encode_message(message)

    lines = ['# {}'.format(data),
             'Channel: Local/{}'.format(extension),
             'Context: gong',
             'Extension: s',
             'Setvar: AUDIO_FILE={}'.format(filepath)]

    callfile_path = os.path.join(tempfile.gettempdir(), message['id'])
    with open(callfile_path, 'w') as f:
        f.writelines("{}\n".format(l) for l in lines)

    if 'start' in message:
        time = int(message['start'].total_seconds())
        os.utime(callfile_path, (time, time))

    new_path = callfile_path(message['id'])
    shutil.move(callfile_path, new_path)


def encode_message(message):
    return json.dumps({'id': message['id'],
                       'description': message['description']})


@delete('/messages/<message_id>')
def delete_message(message_id):
    callfile = callfile_path(message_id)
    audiofile = audio_path(message_id)

    if not all(os.path.exists(callfile), os.path.exists(audiofile)):
        abort(404)

    os.unlink(callfile)
    os.unlink(audiofile)


def generate_audio_file(upload, uid):
    path = audio_path(uid)
    audio.convert_file(upload, path)
    audio.prepend_silence(path, config.get('gong', 'silence'))


def audio_path(uid, exten='.wav'):
    name = "{}{}".format(uid, exten)
    return os.path.join(config.get('gong', 'audio'), name)


def callfile_path(uid):
    name = "xgong_{}".format(uid)
    return os.path.join(config.get('gong', 'callfiles'), name)


def adjust_schedules():
    messages = all_messages()
    scheduled = [messages.pop(0)]

    for message in messages:
        last = scheduled[-1]
        end = last['start'] + audio.file_duration(audio_path(last['uid']))

        if message['start'] <= end:
            message['start'] = end
        scheduled.append(message)

    for message in scheduled:
        path = callfile_path(message['id'])
        time = int(message['start'].total_seconds())
        os.utime(path, (time, time))


def setup():
    audiodir = config.get('gong', 'audio')
    if not os.path.exists(audiodir):
        os.makedirs(audiodir)


if __name__ == "__main__":
    setup()
    run(host='0.0.0.0', port=8000, debug=True, reloader=True)
