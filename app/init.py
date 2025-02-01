from typing import List
from shutil import which
from os import listdir

import app.main as main
from app.lib.environment import PROJECT_DIR, TRAEFIK_NAME, TRAEFIK_NETWORK, TRAEFIK_VOLUME
from app.projects.Project import Project

REQUIRED_PROGRAMS: List[str] = [
    "git",
    "nixpacks"
]

def check_programs() -> List[str]:
    missing_programs: List[str] = []
    for program in REQUIRED_PROGRAMS:
        if which(program) is None:
            missing_programs.append(program)
    return missing_programs

def create_projects() -> dict[str, Project]:
    projects: dict[str, Project] = {}
    for name in listdir(PROJECT_DIR):
        print(f"Imported project {name}")
        projects.update({name: Project(name)})
    return projects

def initialize_traefik():
    if len(main.client.containers.list(filters={"name": TRAEFIK_NAME})) > 0:
        return
    print("Initializing traefik")
    if len(main.client.images.list(filters={"reference": "traefik"})) <= 0:
        print("Pulling traefik image")
        main.client.images.pull("traefik", "latest")
    if len(main.client.networks.list(filters={"name": TRAEFIK_NETWORK})) <= 0:
        print("Creating traefik network")
        main.client.networks.create(TRAEFIK_NETWORK)
    main.client.containers.run(
        image="traefik:latest",
        name=TRAEFIK_NAME,
        restart_policy={"Name": "always"},
        detach=True,
        network=TRAEFIK_NETWORK,
        command=[
            "--providers.docker=true",
            "--entrypoints.http.address=:80",
        ],
        ports={'80/tcp': 80},
        volumes=[
            "/var/run/docker.sock:/var/run/docker.sock",
            f"{TRAEFIK_VOLUME}:/traefik"
        ],
    )

def initialize_database():
    cursor = main.connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, port INTEGER, domain TEXT)")
    cursor.close()

