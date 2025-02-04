from typing import List
import shutil
import os
import warnings
import uuid
import dotenv

import app.main as main
from app.lib.environment import PROJECT_DIR
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
            exit_code, remote = git.get_remote(project_path)
            if exit_code != 0:
                warnings.warn(f"Could not find the remote url to project {project_id}. Assuming there is no remote.")
                remote = None
            exit_code, branch = git.get_branch(project_path)
            if exit_code != 0:
                warnings.warn(f"Could not find the branch name to project {project_id}. Assuming it is 'main'.")
                branch = "main"
            cursor.execute("INSERT INTO projects (id, git_url, branch, port, domain) VALUES (?, ?, ?, ?, ?)",
                           [project_id, remote, branch, 3000, "localhost"])
            env_vars = dotenv.dotenv_values(os.path.join(project_path, ".env"))
            for key, value in env_vars.items():
                cursor.execute("INSERT OR IGNORE INTO environments (id, key, value) VALUES (?, ?, ?)", [project_id, key, value])
    main.connection.commit()

    for db_id in db_ids:
        if db_id not in path_ids:
            warnings.warn(f"Could not find project {db_id}'s files. Cloning it now.")
            git_url, branch = cursor.execute("SELECT git_url, branch FROM projects WHERE id = ?", [db_id]).fetchone()
            git.clone_repo_branch(git_url, branch, str(os.path.join(PROJECT_DIR, db_id)))
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

def initialize_database():
    """
    Creates database tables if they don't exist.
    """
    cursor = main.connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, git_url TEXT, branch TEXT, port INTEGER, domain TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS environments(id TEXT, key TEXT, value TEXT, FOREIGN KEY (id) REFERENCES projects(id) PRIMARY KEY (id, key))")
    cursor.close()

