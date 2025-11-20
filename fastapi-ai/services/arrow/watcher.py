import time, asyncio

from .registry import arrow_registry
from routers import ws


class ArrowWatcher:

    def __init__(self, check_interval=0.1):
        self.running = False
        self.task = None
        self.check_interval = check_interval

    async def start(self):
        if self.running:
            return

        self.running = True
        self.task = asyncio.create_task(self._watch_loop())
        print("[ARROW] Watcher started")

    async def stop(self):
        self.running = False

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                print("[ARROW] Watcher cancelled")

    async def _watch_loop(self):
        while self.running:
            try:
                for cam_id, arrow_service in arrow_registry.items():
                    if arrow_service.is_idle():
                        hit = arrow_service.find_hit_point()

                        if hit is not None:
                            print(f"[HIT] cam={cam_id}, point={hit}")
                            arrow_service.last_hit_time = time.time()

                            await ws.broadcast(cam_id, {"type": "hit", "tip": hit})

                        arrow_service.clear_buffer()
            except Exception as e:
                print(f"[ARROW Watcher] Watcher error: {e}")
                import traceback

                traceback.print_exc()

            await asyncio.sleep(self.check_interval)


arrow_watcher = ArrowWatcher()
