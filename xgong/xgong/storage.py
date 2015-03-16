import json
import os
import uuid
import tempfile
import shutil

from datetime import datetime

from config import load_config

config = load_config()


def all_messages():
    callfile_dir = config.get('xgong', 'callfiles')

    files = (os.path.join(callfile_dir, f)
             for f in os.listdir(callfile_dir)
             if f.startswith('xgong'))

    return (load_message(f) for f in files)


def load_message(path):
    start = datetime.fromtimestamp(os.path.getmtime(path))
    with open(path) as f:
        data = f.readline()[2:]
        data = json.loads(data)
        data['start'] = start

    return data


def save_upload(upload):
    _, extension = os.path.splitext(upload.filename)
    upload_path = tmp_path(extension)
    upload.save(upload_path)
    return upload_path


def add_callfile(message):
    default_extension = config.get('xgong', 'extension')
    max_retries = config.get('xgong', 'max_retries')
    retry_time = config.get('xgong', 'retry_time')

    extension = message.get('extension') or default_extension
    file_path = audio_path(message['id'], '')
    encoded_message = encode_message(message)

    lines = ['# {}'.format(encoded_message),
             'Channel: Local/{}'.format(extension),
             'Context: xgong',
             'Extension: s',
             'MaxRetries: {}'.format(max_retries),
             'RetryTime: {}'.format(retry_time),
             'Setvar: AUDIO_FILE={}'.format(file_path)]

    callfile = os.path.join(config.get('xgong', 'tmp_callfiles'), message['id'])
    with open(callfile, 'w') as f:
        f.writelines("{}\n".format(l) for l in lines)

    if 'start' in message:
        time = int(message['start'].strftime("%s"))
        os.utime(callfile, (time, time))

    new_path = callfile_path(message['id'])
    shutil.move(callfile, new_path)


def audio_path(uid, exten='.wav'):
    name = "{}{}".format(uid, exten)
    return os.path.join(config.get('xgong', 'audio'), name)


def callfile_path(uid):
    name = "xgong_{}".format(uid)
    return os.path.join(config.get('xgong', 'callfiles'), name)


def tmp_path(extension):
    filename = "{}.{}".format(str(uuid.uuid4()), extension)
    return os.path.join(tempfile.gettempdir(), filename)


def encode_message(message):
    return json.dumps({'id': message['id'],
                       'description': message['description'],
                       'extension': message.get('extension')})
