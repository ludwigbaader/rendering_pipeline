import os
import flask
from functools import wraps

import src.blender_commands as blend


USERNAME = "ludwig"
PASSWORD = "test"
PROJECT = "hand_job"


app = flask.Flask(__name__)

def check_authentication(username: str | None, password: str | None) -> bool:
    # return username == os.environ["PIPELINE_USERNAME"] and password == os.environ["PIPELINE_PASSWORD"]
    return username == USERNAME and password == PASSWORD

def request_authentication():
    return (
        'Authentication required', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # get authentication header
        auth = flask.request.authorization

        # if no authentication header is provided or the username and password isn't correct, deny authentication
        if not auth or not check_authentication(auth.username, auth.password):
            return request_authentication()

        return f(*args, **kwargs)
    
    return decorated


project = blend.BlenderProject("hand_job")

@app.route('/')
@requires_auth
def index():
    return flask.render_template(
        'index.html',
        project_name=project.name,
        render_files=project.blend_files,
        active_render_file=project.active_render_file,
        render_is_running=project.render_is_running(),
        render_progress="%.2f" % (100 * project.progress)
    )

@app.route('/update-status', methods=['POST'])
@requires_auth
def update_status():
    task = flask.request.form.get("task")
    print(task)

    if task == "stop_render":
        project.stop_active_render()
    if task == "start_render":
        start_frame = flask.request.form.get("start_frame")
        render_file = flask.request.form.get("render_file")

        if render_file is not None and start_frame is not None:
            project.start_render(render_file, int(start_frame))

    return flask.render_template(
        'index.html',
        project_name=project.name,
        render_files=project.blend_files,
        active_render_file=project.active_render_file,
        render_is_running=project.render_is_running(),
        render_progress="%.2f" % (100 * project.progress)
    )

