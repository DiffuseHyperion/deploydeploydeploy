import os
from typing import Tuple, Dict, Callable

import docker.errors
import fastapi

from app.lib.environment import PROJECT_DIR, TRAEFIK_HTTP_ENTRYPOINT, TRAEFIK_NETWORK, TRAEFIK_HTTPS_ENTRYPOINT, TRAEFIK_CERTRESOLVER
from app import main
from app.lib import nixpacks, git

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

    def invoke_method(self, method: Callable[[], Tuple[int, str] | None], response: fastapi.Response) -> Dict:
        if (error := method()) is None:
            return {
                "project_id": self.project_id,
            }
        else:
            response.status_code = error[0]
            return {
                "error": error[1]
            }

    def build_image(self) -> Tuple[int, str] | None:
        exit_code, output = nixpacks.build_image(self.project_id, self.project_path)
        self.built = True
        return None if exit_code == 0 else (500, output)

    def delete_image(self) -> Tuple[int, str] | None:
        try:
            main.client.images.get(self.project_id).remove()
            self.built = False
            return None
        except docker.errors.ImageNotFound:
            return 400, f"Could not find image to project {self.project_id}"

    def start_container(self) -> Tuple[int, str] | None:
        if self.running:
            return 400, f"Project {self.project_id} is already running"

        cursor = main.connection.cursor()
        domain = cursor.execute("SELECT domain FROM projects WHERE id = ?", [self.project_id]).fetchone()[0]
        port = cursor.execute("SELECT port FROM projects WHERE id = ?", [self.project_id]).fetchone()[0]
        cursor.close()
        labels = {
            "traefik.enable": "true",
            f"traefik.http.routers.http-{self.project_id}.entrypoints": TRAEFIK_HTTP_ENTRYPOINT,
            f"traefik.http.routers.http-{self.project_id}.service": f"http-{self.project_id}",
            f"traefik.http.routers.http-{self.project_id}.rule": f"Host(`{domain}`)",
            f"traefik.http.services.http-{self.project_id}.loadbalancer.server.port": str(port),
        }
        if TRAEFIK_HTTPS_ENTRYPOINT is not None:
            labels = dict(labels, **{
                "traefik.http.middlewares.gzip.compress": "true",
                "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme": "true",
                f"traefik.http.routers.https-{self.project_id}.entrypoints": TRAEFIK_HTTPS_ENTRYPOINT,
                f"traefik.http.routers.https-{self.project_id}.service": f"https-{self.project_id}",
                f"traefik.http.routers.https-{self.project_id}.rule": f"Host(`{domain}`)",
                f"traefik.http.services.https-{self.project_id}.loadbalancer.server.port": str(port),
                f"traefik.http.routers.https-{self.project_id}.middlewares": "gzip",
                f"traefik.http.routers.https-{self.project_id}.tls": "true",
                f"traefik.http.routers.https-{self.project_id}.tls.certresolver": TRAEFIK_CERTRESOLVER,
            })
        try:
            main.client.containers.run(
                image=self.project_id,
                name=self.project_id,
                auto_remove=True,
                detach=True,
                network=TRAEFIK_NETWORK,
                labels=labels
            )
            self.running = True
            return None
        except docker.errors.ImageNotFound:
            return 400, f"Project {self.project_id} has not been built"
        except docker.errors.APIError:
            return 500, f"Could not communicate with Docker API"

    def stop_container(self) -> Tuple[int, str] | None:
        try:
            container = main.client.containers.get(self.project_id)
            container.stop()
            self.running = False
            return None
        except docker.errors.NotFound:
            return 400, f"Project {self.project_id} is not running"
        except docker.errors.APIError:
            return 500, f"Could not communicate with Docker API"

    def update_project(self) -> Tuple[int, str] | None:
        exit_code, response = git.fetch(self.project_path)
        if exit_code != 0:
            return 500, "Could not fetch latest commit"
        exit_code, response = git.reset_hard(self.project_path)
        if exit_code != 0:
            return 500, "Could not hard reset to latest commit"
        return None

    def deploy_project(self) -> Tuple[int, str] | None:
        def invoke_method(method: Callable[[], Tuple[int, str] | None]):
            response = method()
            if response is not None:
                return response

        if self.running:
            if (result := invoke_method(self.stop_container)) is not None:
                return result
        if self.built:
            if (result := invoke_method(self.delete_image)) is not None:
                return result
        if (result := invoke_method(self.update_project)) is not None:
            return result
        if (result := invoke_method(self.build_image)) is not None:
            return result
        if (result := invoke_method(self.start_container)) is not None:
            return result
        return None