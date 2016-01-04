import requests
import os
import json
import re
import logging

from ConfigParser import ConfigParser

logger = logging.getLogger(__name__)
config = ConfigParser()

CONFIG_PATH = '/etc/xgong/jenkins.ini'
FAIL_REGEX = re.compile(r"^(red|yellow)")


def get_failed_jobs():
    jobs = fetch_jobs()
    return filter_failed_jobs(jobs)


def fetch_jobs():
    url = "{}/api/json".format(config.get('jenkins', 'url'))
    response = requests.get(url)
    return response.json()['jobs']


def filter_failed_jobs(jobs):
    return [job['name']
            for job in jobs if FAIL_REGEX.match(job['color'])]


def load_old_jobs():
    path = config.get('jenkins', 'history')
    if not os.path.exists(path):
        return []

    with open(path) as f:
        return json.loads(f.read())


def combine_jobs(old, new):
    with open(config.get('jenkins', 'history'), mode='w') as f:
        f.write(json.dumps(new))

    return set(new) - set(old)


def log_failed_jobs(jobs):
    logger.info("failed jobs: %s", ', '.join(jobs))


def announce_jobs(jobs):
    sentences = build_messages(jobs)
    message = ". ".join(sentences)
    send_message(message)


def build_messages(jobs):
    for job in jobs:
        tpl = config.get('jenkins', 'message')
        yield tpl.format(job=job)


def send_message(message):
    url = config.get('jenkins', 'xgong_url')
    cleaned_message = message.replace("-", " ").replace("_", " ")
    requests.post(url + "/messages/tts/add", data={'text': cleaned_message})


def main():
    config.read([CONFIG_PATH])

    new_jobs = get_failed_jobs()
    old_jobs = load_old_jobs()
    failed_jobs = combine_jobs(old_jobs, new_jobs)

    if failed_jobs:
        log_failed_jobs(failed_jobs)
        announce_jobs(failed_jobs)


if __name__ == '__main__':
    main()
