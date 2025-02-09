import shutil, subprocess

NIXPACK_PATH = shutil.which('nixpacks')

def build_image(name: str, path: str) -> (int, str):
    process = subprocess.run(["nixpacks", "build", "--docker-host", "unix:///var/run/docker.sock", "-n", name, path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout.decode().rstrip()

def build_image_async(name: str, path: str) -> subprocess.Popen:
    return subprocess.Popen(["nixpacks", "build", "--docker-host", "unix:///var/run/docker.sock", "-n", name, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)