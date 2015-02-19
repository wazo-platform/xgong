import pytz
import uuid
import os
import audio
import subprocess

from datetime import datetime
from bottle import run, request, post, get, delete, abort
from ConfigParser import ConfigParser

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

config = ConfigParser()
config.read(['/etc/xgong/config.ini'])

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
TIMEZONE = pytz.timezone(config.get('gong', 'timezone'))

scheduler = BackgroundScheduler()


@get('/messages')
def list_messages():
    return {'messages': tuple(map_job(j) for j in sorted_jobs())}


@post('/messages/add')
def add_message():
    if 'audio' not in request.files:
        abort(400, 'missing audio file')

    message = {'description': request.forms.get('description', ''),
               'id': str(uuid.uuid4())}
    generate_audio_file(request.files['audio'], message['id'])

    if 'timestamp' in request.forms:
        timestamp = datetime.strptime(request.forms.get('timestamp'),
                                      DATETIME_FORMAT)
        job = scheduler.add_job(play_message, 'date',
                                args=(message,),
                                run_date=timestamp,
                                timezone=TIMEZONE)
        adjust_schedules()
    else:
        job = scheduler.add_job(play_message,
                                args=(message,),
                                timezone=TIMEZONE)

    return map_job(job)


@delete('/messages/<message_id>')
def delete_message(message_id):
    found = [j for j in scheduler.get_jobs() if j.args[0]['id'] == message_id]
    if not found:
        abort(404)

    for job in found:
        scheduler.remove_job(job.id)


def map_job(job):
    message = dict(job.args[0])
    message['start'] = job.next_run_time.strftime(DATETIME_FORMAT)
    return message


def sorted_jobs():
    return sorted(scheduler.get_jobs(), key=lambda j: j.next_run_time)


def play_message(message):
    path = audio_path(message['id'])
    new_path = '/tmp/xgong.wav'
    os.rename(path, new_path)

    originate = 'channel originate Local/{extension} extension s@xgong'
    cmd = ['asterisk', '-rx', originate.format(extension=config.get('gong', 'extension'))]
    subprocess.check_call(cmd)


def generate_audio_file(upload, uid):
    path = audio_path(uid)
    audio.convert_file(upload, path)
    audio.prepend_silence(path, config.get('gong', 'silence'))


def audio_path(uid):
    return os.path.join(config.get('gong', 'audio'), "{}.wav".format(uid))


def adjust_schedules():
    messages = [{'job_id': job.id,
                 'uid': job.args[0]['id'],
                 'start': job.next_run_time}
                for job in sorted_jobs()]
    scheduled = [messages.pop(0)]

    for message in messages:
        last = scheduled[-1]
        end = last['start'] + audio.file_duration(audio_path(last['uid']))

        if message['start'] <= end:
            message['start'] = end
        scheduled.append(message)

    for message in scheduled:
        scheduler.reschedule_job(message['job_id'], trigger='date',
                                 run_date=message['start'], timezone=TIMEZONE)


def setup():
    audiodir = config.get('gong', 'audio')
    if not os.path.exists(audiodir):
        os.makedirs(audiodir)

    database = config.get('gong', 'database')[10:]
    if not os.path.exists(database):
        open(database, 'a').close()

    jobstores = {'default': SQLAlchemyJobStore(url=config.get('gong', 'database'))}
    scheduler.configure(jobstores=jobstores)


if __name__ == "__main__":
    setup()
    scheduler.start()
    run(host='0.0.0.0', port=8000, debug=True, reloader=True)
