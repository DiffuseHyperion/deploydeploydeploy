import os

from app.lib.environment import PROJECT_DIR
import app.main as main

class Project(object):
    """
    Fields here should change if the database file is moved to another computer. If not, it belongs in the database.
    Exception is project id (identifier kinna important), and project path (because im lazy)
    """
    project_id: str
    project_path: str
    running: bool
    built: bool

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.project_path = os.path.join(PROJECT_DIR, project_id)
        self.running = len(main.client.containers.list(filters={'name': project_id})) > 0
        self.built = len(main.client.images.list(filters={'reference': project_id})) > 0