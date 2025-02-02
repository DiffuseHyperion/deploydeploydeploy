import shutil, subprocess

GIT_PATH = shutil.which('git')

def clone_repo(url: str, path: str) -> (int, str):
    process = subprocess.run([GIT_PATH, 'clone', url, path], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout.decode().rstrip()

def get_remote(path: str) -> (str, (int, str)):
    process = subprocess.run([GIT_PATH, 'config', "--get", "remote.origin.url"], cwd=path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout.decode().rstrip()

