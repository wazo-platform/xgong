import requests
import os
import json
import datetime
import re
import subprocess

from ConfigParser import ConfigParser

CONFIG_PATH = '/etc/jenkins-gong/config.ini'
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


def print_failed_jobs(jobs):
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("{} failed jobs: {}".format(stamp,
                                      ', '.join(jobs)))


def ring_gong(extension, macro):
    command = ['asterisk', '-rx', 'channel originate {} {}'.format(extension, macro)]
    subprocess.check_call(command)


def main():
    config = load_config(CONFIG_PATH)

    jenkins_url = config.get('jenkins-gong', 'url')
    history = config.get('jenkins-gong', 'history')
    extension = config.get('jenkins-gong', 'extension')
    macro = config.get('jenkins-gong', 'macro')

    jobs = fetch_jobs(jenkins_url)
    failed = filter_failed_jobs(jobs)
    new_failed = new_failed_jobs(failed, history)

    if new_failed:
        print_failed_jobs(new_failed)
        ring_gong(extension, macro)


if __name__ == '__main__':
    main()
