import shutil, subprocess

GIT_PATH = shutil.which("git")

def clone_repo_branch(git_url: str, branch: str, path: str) -> (int, str):
    process = subprocess.run([GIT_PATH, "clone", "-b", branch, git_url, path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout.decode().rstrip()

def get_remote(path: str) -> (int, str):
    process = subprocess.run([GIT_PATH, "config", "--get", "remote.origin.url"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout.decode().rstrip()

def get_branch(path: str) -> (int, str):
    process = subprocess.run([GIT_PATH, "rev-parse", "--abbrev-ref", "HEAD"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout.decode().rstrip()

def fetch(path: str) -> (int, str):
    process = subprocess.run([GIT_PATH, "fetch"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout.decode().rstrip()

def reset_hard(path: str) -> (int, str):
    process = subprocess.run([GIT_PATH, "reset", "--hard"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout.decode().rstrip()