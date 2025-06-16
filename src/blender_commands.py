import json
import os
from subprocess import Popen


BLENDER_DIR = "C:\\Program Files\\Blender Foundation"
IMAGE_FORMATS = ["png", "exr", "jpg", "jpeg"]


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
        self.blend_files = [filename for filename in files if ".blend" in filename and ".blend1" not in filename]

        self.active_render_file = None
        
        self.file_info = dict()

    def render_is_running(self) -> bool:
        return self.active_render_file is not None and self.active_render_process is not None

    def stop_active_render(self) -> str:
        if self.active_render_process is None:
            return "No active render is running."
        
        self.active_render_process.kill()

        self.active_render_process = None
        self.active_render_file = None

        return "Stopped active render."

    def start_render(self, filename: str, start_frame: int | None = None):
        # check if the data has already been read out
        if filename not in self.file_info.keys():
            self.read_file_info(filename)

        # construct command argument string
        args = [BLENDER_DIR, "-b", os.path.join(self.directory, filename)]
        if start_frame is not None:
            args.extend(["-s", str(start_frame)])
        args.append("-a")
        
        # start a subprocess running blender
        self.active_render_process = Popen(args)
        self.active_render_file = filename
    
    def read_file_info(self, filename: str) -> dict:
        # open the specified file in blender with a readout script and read results
        python_script_dir = os.path.dirname(os.path.abspath(__file__))
        tmp_readout_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projects/tmp/blend_readout_tmp.json")

        args = [
            BLENDER_DIR, "-b", os.path.join(self.directory, filename), 
            "-P", os.path.join(python_script_dir, "blender_scripts/read_blend_data.py"),
            "--", tmp_readout_path
        ]
        blend_process = Popen(args)
        blend_process.wait()

        # read results from readout
        f = open(tmp_readout_path, 'r')
        data_readout = json.loads(f.read())
        f.close()

        self.file_info[filename] = data_readout
        return data_readout
    
    def check_active_render_progress(self) -> float:
        # TODO - add more granular progress updates checking the std output of the running process

        main_output = self.file_info[self.active_render_file]["main_output_path"]
        composite_outputs = self.file_info[self.active_render_file]["composite_output_paths"]

        # only if there are no composite output, check the main output
        if len(composite_outputs) == 0:
            composite_outputs.append(main_output)

        # check how many files have already been stored
        total_frames = self.file_info[self.active_render_file]["end_frame"] - self.file_info[self.active_render_file]["start_frame"]

        existing_frames = []
        for output_path in composite_outputs:
            directory = os.path.dirname(output_path)
            for filename in os.listdir(directory):
                if filename.split(".")[-1] in IMAGE_FORMATS:
                    index = filename.split("_")[-1].split(".")[0] # assumption that index is the last part of the filename before the file extension, separated by an underscore
                    existing_frames.append(int(index))
        
        # each frame index has to be as many times in the list as there are output paths
        completed_frames = []
        for frame_id in existing_frames:
            if existing_frames.count(frame_id) == len(composite_outputs):
                completed_frames.append(frame_id)
        
        # make completed_frames unique
        completed_frames = list(set(completed_frames))

        return completed_frames / total_frames
        