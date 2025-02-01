import os

from dotenv import dotenv_values

from app.lib.environment import PROJECT_DIR
import app.main as main

class Project(object):
    project_id: str
    project_path: str
    running: bool
    built: bool
    env_vars: dict[str, str | None]

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.project_path = os.path.join(PROJECT_DIR, project_id)
        self.running = len(main.client.containers.list(filters={'name': project_id})) > 0
        self.built = len(main.client.images.list(filters={'reference': project_id})) > 0
        self.env_vars = dotenv_values(os.path.join(self.project_path, '.env'))
