from typing import List
import shutil
import os
import warnings
import uuid
import dotenv

import app.main as main
from app.lib.environment import PROJECT_DIR, TRAEFIK_NAME, TRAEFIK_NETWORK, TRAEFIK_VOLUME, TRAEFIK_EMAIL, \
    TRAEFIK_CERTS, TRAEFIK_STAGING, TRAEFIK_HTTPS
from app.projects.Project import Project
from app.lib import git

REQUIRED_PROGRAMS: List[str] = [
    "git",
    "nixpacks"
]

def check_programs() -> List[str]:
    """
    Checks if all required programs are installed.
    :return: Names of required programs that are not installed.
    """
    missing_programs: List[str] = []
    for program in REQUIRED_PROGRAMS:
        if shutil.which(program) is None:
            missing_programs.append(program)
    return missing_programs

def synchronize_projects():
    """
    Attempt to fix any de-synchronization between the projects in the database and the project files on disk.
    If a project is found in the database but not on disk, the project will be cloned again
    If a project is found on disk but not in the database, the project will be added into the database
    """
    cursor = main.connection.cursor()
    db_ids = [id_tuple[0] for id_tuple in cursor.execute("SELECT id FROM projects").fetchall()]

    path_ids = []
    for project_id in os.listdir(PROJECT_DIR):
        try:
            uuid.UUID(project_id, version=4)
        except ValueError:
            warnings.warn("A folder named an invalid project ID was found within the projects directory. Skipping.")
            continue
        project_path = os.path.join(PROJECT_DIR, project_id)
        if not os.path.exists(os.path.join(project_path, ".git")):
            warnings.warn(f"A project folder with the id {project_id} is not a git repository. Skipping.")
            continue

        path_ids.append(project_id)
        if project_id not in db_ids:
            warnings.warn(f"A project folder with the ID {project_id} is not in the database. Adding it to the database now.")
            exit_code, output = git.get_remote(project_path)
            if exit_code != 0:
                warnings.warn(f"Could not find the remote url to project {project_id}. Assuming there is no remote.")
                output = None
            cursor.execute("INSERT INTO projects (id, git_url, port, domain) VALUES (?, ?, ?, ?)",
                           [project_id, output, 3000, "localhost"])
            env_vars = dotenv.dotenv_values(os.path.join(project_path, ".env"))
            for key, value in env_vars.items():
                cursor.execute("INSERT INTO environments (id, key, value) VALUES (?, ?, ?)", [project_id, key, value])
    main.connection.commit()

    for db_id in db_ids:
        if db_id not in path_ids:
            warnings.warn(f"Could not find project {db_id}'s files. Cloning it now.")
            git_url = cursor.execute("SELECT git_url FROM projects WHERE id = ?", [db_id]).fetchone()[0]
            git.clone_repo(git_url, str(os.path.join(PROJECT_DIR, db_id)))
            env_vars = cursor.execute("SELECT key, value FROM environments WHERE id = ?", [db_id]).fetchall()
            env_path = os.path.join(PROJECT_DIR, db_id, ".env")
            if len(env_vars) > 0 and not os.path.exists(env_path):
                with open(env_path, "w") as _:
                    pass
            for key, value in env_vars:
                dotenv.set_key(str(env_path), key, value)
    cursor.close()

def create_projects() -> dict[str, Project]:
    """
    Returns a dictionary of all project ids to a Project object.
    :return:
    """
    projects: dict[str, Project] = {}
    for name in os.listdir(PROJECT_DIR):
        projects.update({name: Project(name)})
    return projects

def initialize_traefik():
    """
    Initializes the traefik container, network and volume, based on environment variables.
    """
    if len(main.client.containers.list(filters={"name": TRAEFIK_NAME})) > 0:
        return
    print("Initializing traefik")
    if len(main.client.images.list(filters={"reference": "traefik"})) <= 0:
        print("Pulling traefik image")
        main.client.images.pull("traefik", "latest")
    if len(main.client.networks.list(filters={"name": TRAEFIK_NETWORK})) <= 0:
        print("Creating traefik network")
        main.client.networks.create(TRAEFIK_NETWORK)

    commands = [
        "--providers.docker=true",
        "--entrypoints.http.address=:80"
    ]
    volumes = [
        "/var/run/docker.sock:/var/run/docker.sock",
        f"{TRAEFIK_VOLUME}:/traefik",
    ]
    ports = {
        "80/tcp": 80,
    }
    if TRAEFIK_HTTPS:
        commands.extend([
            "--entrypoints.https.address=:443",
            "--certificatesresolvers.letsencrypt.acme.tlschallenge=true",
            f"--certificatesresolvers.letsencrypt.acme.email={TRAEFIK_EMAIL}",
            "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json",
            f"--certificatesresolvers.letsencrypt.acme.caserver={
            ("https://acme-staging-v02.api.letsencrypt.org/directory" if TRAEFIK_STAGING
             else "https://acme-v02.api.letsencrypt.org/directory")}"
        ])
        volumes.append(
            f"{TRAEFIK_CERTS}:/letsencrypt"
        )
        ports.update({
            "443/tcp": 443,
        })
    if TRAEFIK_STAGING:
        warnings.warn("TRAEFIK_STAGING was set to true. Traefik will use Let's Encrypt staging environment.")
    main.client.containers.run(
        image="traefik:latest",
        name=TRAEFIK_NAME,
        restart_policy={"Name": "always"},
        detach=True,
        network=TRAEFIK_NETWORK,
        command=commands,
        ports=ports,
        volumes=volumes,
    )

def initialize_database():
    """
    Creates database tables if they don't exist.
    """
    cursor = main.connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, git_url TEXT, port INTEGER, domain TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS environments(id TEXT, key TEXT, value TEXT, FOREIGN KEY (id) REFERENCES projects(id) PRIMARY KEY (id, key))")
    cursor.close()

