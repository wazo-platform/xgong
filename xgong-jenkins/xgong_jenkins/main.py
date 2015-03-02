import requests
import os
import json
import re
import logging
from xgong_jenkins import tts


from ConfigParser import ConfigParser
logger = logging.getLogger(__name__)

CONFIG_PATH = '/etc/xgong/config.ini'
FAIL_REGEX = re.compile(r"^(red|yellow)")


def load_config(filepath):
    parser = ConfigParser()
    parser.readfp(open(filepath))
    return parser


def fetch_jobs(url):
    response = requests.get(url)
    data = json.loads(response.text)
    return data['jobs']


def filter_failed_jobs(jobs):
    return [job['name'] for job in jobs if FAIL_REGEX.match(job['color'])]


def new_failed_jobs(failed_jobs, history):
    old_jobs = fetch_old_jobs(history)

    with open(history, mode='w') as f:
        f.write(json.dumps(failed_jobs))

    return set(failed_jobs) - set(old_jobs)


def fetch_old_jobs(history):
    if not os.path.exists(history):
        return []

    with open(history) as f:
        return json.loads(f.read())


def log_failed_jobs(jobs):
    logger.info("failed jobs: %s", ', '.join(jobs))


def send_message(failed, url, preface):
    names = [n.replace("-", " ").replace("_", " ") for n in failed]
    files = [preface] + [tts.generate(n) for n in names]
    filepath = tts.merge_files(files)

    upload = {'audio': ('audio.mp3', open(filepath, 'rb'))}
    requests.post(url + "/messages/add", files=upload)

    for path in files + [filepath]:
        os.unlink(path)


def main():
    config = load_config(CONFIG_PATH)

    jenkins_url = config.get('jenkins', 'url')
    history = config.get('jenkins', 'history')
    gong_url = config.get('jenkins', 'xgong_url')
    preface = config.get('jenkins', 'preface')

    jobs = fetch_jobs(jenkins_url)
    failed = filter_failed_jobs(jobs)
    new_failed = new_failed_jobs(failed, history)

    if new_failed:
        log_failed_jobs(new_failed)
        send_message(new_failed, gong_url, preface)


if __name__ == '__main__':
    main()
