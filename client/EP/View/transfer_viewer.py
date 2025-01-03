from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import threading
import uvicorn
from fastapi.responses import StreamingResponse
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from ..manager import BaseClient
from ..configs import Config


class TransferViewer:
    def __init__(self, invoker: BaseClient):
        self.invoker = invoker

        self.app = FastAPI(lifespan=self.lifesapen)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.register_interaction()

        self.thread = None
        self.loop = None

    @asynccontextmanager
    async def lifesapen(self, app: FastAPI):
        asyncio.create_task(self.invoker.init())
        yield
        await self.invoker.close()

    def register_interaction(self):
        frontend_dist = Path("frontend")
        self.app.mount("/assets", StaticFiles(directory=frontend_dist / 'assets', html=True), name="frontend")
        
        @self.app.get("/")
        async def index():
            return FileResponse(str(frontend_dist / "index.html"))
        
        @self.app.get('/favicon.ico')
        async def favicon():
            return FileResponse(str(frontend_dist / 'favicon.ico'))

        @self.app.post("/api/register")
        async def register():
            state, msg = await self.invoker.register()
            return {"state": state, "msg": msg}

        @self.app.get("/api/queryRegistered")
        async def query_registered():
            return {
                "state": self.invoker.registered,
                "msg": "Registered" if self.invoker.registered else "Not registered",
            }

        @self.app.post("/api/get_action")
        async def get_action(request: Request):
            data = await request.json()
            instruction = data["instruction"]

            state, msg = await self.invoker.get_action(instruction)
            return {"state": state, "msg": msg}

        @self.app.get("/api/queryInited")
        def query_inited():
            ws, env = self.invoker.check_init()
            if not ws and not env:
                return {"state": False, "msg": "Both Not inited"}
            elif not ws:
                return {"state": False, "msg": "WS not inited"}
            elif not env:
                return {"state": False, "msg": "Env not inited"}
            else:
                return {"state": True, "msg": "Both inited"}

        @self.app.get("/api/queryEnvironment")
        def query_environment():
            state, info = self.invoker.get_env_info()
            out = {"state": state}
            out.update(info)
            return out

        @self.app.post("/api/startTask")
        async def start_task(request: Request):
            data = await request.json()
            instruction = data["instruction"]

            state, msg = self.invoker.start_task(instruction)

            return {
                "state": state,
                "msg": msg,
            }

        @self.app.post("/api/stopTask")
        def stop_task():
            state, msg = self.invoker.stop_task()
            return {
                "state": state,
                "msg": msg,
            }

        @self.app.get("/api/queryTaskState")
        def query_task_state():
            return {
                "state": self.invoker.task_running,
                "msg": (
                    "Task running" if self.invoker.task_running else "Task not running"
                ),
            }

        @self.app.get("/api/queryIframeUrl")
        def query_iframe_url():
            state, url = self.invoker.get_live_url()
            return {"state": state, "msg": url}
        
        @self.app.post("/api/startPushVideo")
        def start_push_video():
            state, msg = self.invoker.start_push_video()
            return {"state": state, "msg": msg}
        
        @self.app.post("/api/stopPushVideo")
        def stop_push_video():
            state, msg = self.invoker.stop_push_video()
            return {"state": state, "msg": msg}
        
        @self.app.get('/api/getVideo')
        def get_video():
            return StreamingResponse(self.invoker.get_video_pushing_source(), media_type="multipart/x-mixed-replace; boundary=frame")

        @self.app.post("/api/resetScene")
        async def reset_scene():
            state, msg = await self.invoker.reset_scene()
            return {"state": state, "msg": msg}

    def run(self):
        def f():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            config = uvicorn.Config(self.app, host="localhost", port=Config.VIEWER_PORT)
            server = uvicorn.Server(config)
            self.loop.run_until_complete(server.serve())

        self.thread = threading.Thread(target=f, daemon=True)
        self.thread.start()

    def close(self):
        self.invoker.close()
