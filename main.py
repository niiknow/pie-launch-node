import asyncio
import logging
import os
import time
from dataclasses import dataclass

from fastapi import BackgroundTasks, FastAPI, Request

logging.basicConfig(
    level=logging.INFO, format="%(levelname)-9s %(asctime)s - %(name)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

BUILD_BASE_DIR = "/builds/"
BUILD_BUFFER = {}

app = FastAPI()
loop = asyncio.get_event_loop()


app = FastAPI()


@dataclass
class Build:
    build_name: str
    buildy_sequence: str
    build_id: str = None
    status: str = "pending"

    def __post_init__(self):
        self.build_id = str(time.time())
        self.build_dir = os.path.join(BUILD_BASE_DIR, self.build_id)
        # os.makedirs(self.experiment_dir, exist_ok=False) # Commented out for testing

    async def run(self):
        self.status = "running"
        await asyncio.sleep(5)  # simulate long running build
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
    LOGGER.info(f"root - added task")
    return {
        "Build created": build,
        "Build ID": build.build_id,
        "Backlog Length": len(BUILD_BUFFER),
    }


def process(build: Build):
    """Schedule processing of build, and then run some long running non-IO job without blocking the app"""
    asyncio.run_coroutine_threadsafe(aprocess(build), loop)
    LOGGER.info(
        f"process - {build.build_id} - Submitted build job. Now run non-IO work for 10 seconds..."
    )
    time.sleep(
        10
    )  # simulate long running non-IO work, does not block app as this is in another thread - provided it is not cpu bound.
    LOGGER.info(f"process - {build.experiment_id} - wake up!")


async def aprocess(build):
    """Process build and generate data"""
    ret_code = await build.run()
    del BUILD_BUFFER[build.build_id]
    LOGGER.info(
        f"aprocess - Build {build.build_id} processing finished with return code {ret_code}."
    )
