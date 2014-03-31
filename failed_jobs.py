import requests
import os
import json
import sys
import datetime

URL = "http://jenkins.server.com/api/json"
PERSIST = "/tmp/last_failed_jobs.json"


def fetch_jobs(url):
    response = requests.get(url)
    return response.json()


def filter_failed_jobs(jobs):
    return [job['name'] for job in jobs if job['color'] in ['red', 'yellow']]


def new_failed_jobs(failed_jobs):
    old_jobs = fetch_old_jobs()

    with open(PERSIST, mode='w') as f:
        f.write(json.dumps(failed_jobs))

    return set(failed_jobs) - set(old_jobs)


def fetch_old_jobs():
    if not os.path.exists(PERSIST):
        return []

    with open(PERSIST) as f:
        return json.loads(f.read())


def print_failed_jobs(jobs):
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("{} failed jobs: {}".format(stamp,
                                      ', '.join(jobs)))


if __name__ == '__main__':
    response = fetch_jobs(URL)
    jobs = response['jobs']
    failed = filter_failed_jobs(jobs)
    new_failed = new_failed_jobs(failed)

    if new_failed:
        print_failed_jobs(new_failed)
        sys.exit(1)
