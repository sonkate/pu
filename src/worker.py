from celery import Celery
from src.config import config
import json

import asyncio


class AsyncCelery(Celery):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patch_task()

    def patch_task(self):
        TaskBase = self.Task
        class ContextTask(TaskBase):
            abstract = True
            loop = asyncio.new_event_loop()
            def _run(self, *args, **kwargs):
                result = self.loop.run_until_complete(TaskBase.__call__(self, *args, **kwargs)) 
                return result
            def __call__(self, *args, **kwargs):
                return self._run(*args, **kwargs)
        self.Task = ContextTask

def create_worker():
    _celery = AsyncCelery(__name__, broker=config.BROKER_URL, backend=config.BROKER_URL)
    _conf_json = json.loads(config.model_dump_json())
    _celery.conf.update(_conf_json)
    return _celery

worker = create_worker()