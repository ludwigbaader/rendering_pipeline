import json
import os


class BlenderProject():
    info: dict

    def __init__(self, proj_id: str):
        f = open(f"projects/{proj_id}.json")
        config = json.loads(f.read())
        f.close()

        self.name = config["name"]
        self.directory = config["directory"]
        self.progress = 0

        files = os.listdir(self.directory)
        self.blend_files = [filename for filename in files if ".blend" in filename and not ".blend1" in filename]

        self.active_render_file = None

    def render_is_running(self) -> bool:
        return False

    def stop_active_render(self):
        print("Stopping render.")
        pass

    def start_render(self, file: str, start_frame: int):
        pass