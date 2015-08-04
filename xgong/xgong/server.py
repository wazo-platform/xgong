import uuid
import os
import audio
import storage
import tts

from config import load_config
from datetime import datetime, timedelta
from bottle import run, request, post, get, delete, abort

config = load_config()

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


@get('/messages')
def list_messages():
    messages = tuple(encode_message(m) for m in storage.all_messages())
    return {'messages': messages}


def encode_message(message):
    return {'id': message['id'],
            'description': message['description'],
            'start': message['start'].strftime(DATETIME_FORMAT),
            'extension': message.get('extension')}


@post('/messages/add')
def add_message():
    if 'audio' not in request.files:
        abort(400, 'missing audio file')

    upload_path = storage.save_upload(request.files['audio'])
    audio_path = storage.tmp_path('wav')
    try:
        audio.convert_file(upload_path, audio_path)
        create_message_and_files(audio_path)
    finally:
        os.unlink(upload_path)
        os.unlink(audio_path)


@post('/messages/tts/add')
def add_tts_message():
    if 'text' not in request.forms:
        abort(400, 'missing text')

    apikey = config.get('xgong', 'apikey')
    text = request.forms['text'].decode('utf-8')
    tts_path = tts.generate(text, apikey)
    try:
        create_message_and_files(tts_path)
    finally:
        os.unlink(tts_path)


def create_message_and_files(audio_path):
    message = extract_message()
    prepare_audio(message, audio_path)
    storage.add_callfile(message)
    adjust_schedules()


def extract_message():
    message = {'id': str(uuid.uuid4()),
               'description': request.forms.get('description', ''),
               'extension': request.forms.get('extension')}

    if 'start' in request.forms:
        message['start'] = datetime.strptime(request.forms['start'],
                                             DATETIME_FORMAT)

    return message


@delete('/messages/<message_id>')
def delete_message(message_id):
    callfile_path = storage.callfile_path(message_id)
    audio_path = storage.audio_path(message_id)

    if not all((os.path.exists(callfile_path), os.path.exists(audio_path))):
        abort(404)

    os.unlink(callfile_path)
    os.unlink(audio_path)


def prepare_audio(message, raw_path):
    audio_path = storage.audio_path(message['id'])

    if message.get('extension') is not None:
        silence = config.get('xgong', 'extension_silence')
    else:
        silence = config.get('xgong', 'silence')

    audio.prepend_silence(raw_path, audio_path, silence)


def adjust_schedules():
    messages = list(storage.all_messages())
    scheduled = [messages.pop(0)]

    for message in messages:
        last = scheduled[-1]
        duration = audio.file_duration(storage.audio_path(last['id']))
        end = last['start'] + duration + timedelta(seconds=1)

        if message['start'] <= end:
            message['start'] = end
        scheduled.append(message)

    for message in scheduled:
        path = storage.callfile_path(message['id'])
        time = int(message['start'].strftime("%s"))
        os.utime(path, (time, time))


if __name__ == "__main__":
    run(host='0.0.0.0', port=9600, debug=True, reloader=True)
