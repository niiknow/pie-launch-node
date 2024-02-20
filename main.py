import os
import time
from dataclasses import dataclass

from fastapi import BackgroundTasks, FastAPI, Request

BUILD_BASE_DIR = "/build/"
BUILD_BUFFER = {}


app = FastAPI()


@dataclass
class Build:
    build_sequence: str
    build_id: str = None
    build_dir: str
    status: str = "pending"

    def __post_init__(self):
        self.build_id = str(time.time())
        self.build_dir = os.path.join(BUILD_BASE_DIR, self.build_id)
        os.makedirs(self.build_dir, exist_ok=False)

    def run(self):
        self.status = "running"
        # perform some long task using the build sequence and get a return code #
        self.status = "finished"
        return 0  # or another code depending on the final output


async def process(build: Build):
    """Process build and generate data"""
    ret_code = await build.run()
    del BUILD_BUFFER[build.build_id]
    print(f"Build {build.build_id} processing finished with return code {ret_code}.")


@app.get("/healthcheck")
async def healthcheck():
    """healthcheck endpoint

    Returns:
        string: OK
    """
    return "OK"


@app.post("/build")
async def build(request: Request, background_tasks: BackgroundTasks):
    build_data = await request.body()
    build_data = build_data.decode("utf-8")
    build_data = dict(str(x).split("=") for x in build_data.split("&"))
    build = Build(**build_data)
    BUILD_BUFFER[build.build_id] = build
    background_tasks.add_task(process, build)
    return {
        "Build created": build,
        "Build ID": build.build_id,
        "Backlog Length": len(BUILD_BUFFER),
    }


@app.get("/backlog/")
def return_backlog():
    return {f"Currently {len(BUILD_BUFFER)} jobs in the backlog."}
