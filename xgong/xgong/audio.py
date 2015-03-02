import tempfile
import subprocess
import os
import uuid
import shutil

from datetime import timedelta


def mk_filepath(extension):
    filename = "{}.{}".format(str(uuid.uuid4()), extension)
    return os.path.join(tempfile.gettempdir(), filename)


def convert_file(upload, filepath):
    _, extension = os.path.splitext(upload.filename)
    raw_filepath = mk_filepath(extension)

    upload.save(raw_filepath)

    cmd = ['sox', raw_filepath, '-c', '1', '-r', '8000', filepath]
    subprocess.check_call(cmd)

    os.unlink(raw_filepath)


def prepend_silence(filepath, seconds):
    tmp_filepath = mk_filepath('wav')

    cmd = ['sox', filepath, tmp_filepath, 'pad', '{}@0.00'.format(seconds)]
    subprocess.check_call(cmd)

    shutil.move(tmp_filepath, filepath)


def file_duration(filepath):
    cmd = ['soxi', '-D', filepath]
    output = subprocess.check_output(cmd).strip()
    if output == "0":
        return timedelta(seconds=0)

    seconds = output.split(".", 1)[0]
    return timedelta(seconds=int(seconds))
