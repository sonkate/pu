from fastapi.applications import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.apis import routes
from src.logger import DefaultFormatter
import json
import logging

class Application(FastAPI):
    def __init__(self, *args, **kwargs ) -> None:
        super().__init__(*args, **kwargs)

        async def exc_method_not_allow(request: Request, exc: HTTPException):
            return Response(
                content=json.dumps({
                    'data': '',
                    'msg': 'Method not allow',
                    'error': {}
                }),
                status_code=405,
                headers={'Content-type': 'application/json'}
            )

        async def exc_not_found(request: Request, exc: HTTPException):
            return Response(
                content=json.dumps({
                    'data': '',
                    'msg': 'Not found',
                    'error': {}
                }),
                status_code=404,
                headers={'Content-type': 'application/json'}
            )

        _excs = self.exception_handlers
        self.exception_handlers = {
            **_excs,
            405: exc_method_not_allow,
            404: exc_not_found
        }

app = Application(routes=routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger('uvicorn.access')
    logger.setLevel(logging.DEBUG)
    formatter = DefaultFormatter(
        fmt="%(asctime)s [%(process)s] %(levelprefix)s %(message)s",
        use_colors=True,
        datefmt='%d-%m-%Y %H:%M:%S'
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)