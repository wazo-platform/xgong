import subprocess
import shutil

from datetime import timedelta

from storage import tmp_path


def convert_file(old_path, new_path):
    cmd = ['sox', old_path, '-c', '1', '-r', '8000', new_path]
    subprocess.check_call(cmd)


def prepend_silence(audio_path, seconds):
    new_path = tmp_path('wav')

    cmd = ['sox', audio_path, new_path, 'pad', '{}@0.00'.format(seconds)]
    subprocess.check_call(cmd)

    shutil.move(new_path, audio_path)


def file_duration(audio_path):
    cmd = ['soxi', '-D', audio_path]
    output = subprocess.check_output(cmd).strip()
    if output == "0":
        return timedelta(seconds=0)

    seconds = output.split(".", 1)[0]
    return timedelta(seconds=int(seconds))
