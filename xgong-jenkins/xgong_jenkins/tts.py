import requests
import subprocess
import os
import uuid
import tempfile

GOOGLE_URL = "http://translate.google.com/translate_tts"


class ConversionError(Exception):
    pass


def generate_merge(sentences, language='fr'):
    files = [generate(s, language) for s in sentences]
    filepath = unique_filepath('mp3')
    merge_files(files, filepath)
    return filepath


def generate(sentence, language='fr'):
    if len(sentence) > 100:
        raise ConversionError("sentence too long")

    filepath = unique_filepath('mp3')

    params = {'ie': 'UTF-8', 'tl': language, 'q': sentence.encode('utf8')}
    response = requests.get(GOOGLE_URL, params=params, stream=True)

    if response.status_code != 200:
        raise ConversionError("google translate responded with {}".format(response.status_code))

    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(2 * 1024 * 1024):
            f.write(chunk)

    return filepath


def unique_filepath(extension):
    name = "{}.{}".format(uuid.uuid4(), extension)
    return os.path.join(tempfile.gettempdir(), name)


def merge_files(files):
    filepath = unique_filepath('mp3')
    cmd = ['sox'] + files + [filepath]
    subprocess.check_call(cmd)
    return filepath
