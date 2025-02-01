import shutil
import subprocess

GIT_PATH = shutil.which('git')

def clone_repo(url: str, path: str) -> (int, str):
    process = subprocess.run([GIT_PATH, 'clone', url, path], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout.decode().rstrip()