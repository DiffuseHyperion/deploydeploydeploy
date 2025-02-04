import shutil, subprocess

NIXPACK_PATH = shutil.which('nixpacks')

def build_image(name: str, path: str) -> (int, str):
    process = subprocess.run(["nixpacks", "build", "-n", name, path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout.decode().rstrip()