import requests
import os
import uuid
import tempfile

API_URL = "http://api.voicerss.org"
CHUNK = 2 * 1024 * 1024


def generate(text, apikey, language='fr-fr', aformat='8khz_16bit_mono'):
    params = {'key': apikey,
              'src': text,
              'hl': language,
              'c': 'WAV',
              'f': aformat}

    filepath = unique_filepath('wav')
    response = requests.post(API_URL, data=params, stream=True)
    response.raise_for_status()

    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(CHUNK):
            f.write(chunk)

    return filepath


def unique_filepath(extension):
    name = "{}.{}".format(uuid.uuid4(), extension)
    return os.path.join(tempfile.gettempdir(), name)
