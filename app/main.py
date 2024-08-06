from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.common.error import BadRequest, UnprocessableError, UnauthorizatedError
from app.config import Config
from app.database.mongo import close_db_connect
from app.common.startup import startup
from app.api import admin, users, events

app = FastAPI()

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", close_db_connect)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: Set frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# openapi schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=Config.title,
        version=Config.version,
        routes=app.routes
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# errors handlers
@app.exception_handler(BadRequest)
async def bad_request_handler(req: Request, exc: BadRequest) -> JSONResponse:
    return exc.gen_err_resp()


@app.exception_handler(RequestValidationError)
async def invalid_req_handler(
    req: Request,
    exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "type": "about:blank",
            'title': 'Bad Request',
            'status': 400,
            'detail': [str(exc)]
        }
    )


@app.exception_handler(UnprocessableError)
async def unprocessable_error_handler(
    req: Request,
    exc: UnprocessableError
) -> JSONResponse:
    return exc.gen_err_resp()

@app.exception_handler(UnauthorizatedError)
async def unauthorizated_error_handler(
    req: Request,
    exc: UnauthorizatedError
) -> JSONResponse:
    return exc.gen_err_resp()


# API Path
app.include_router(
    users.router,
    prefix='/users',
    tags=["Users"]
)

app.include_router(
    admin.router,
    prefix='/admin',
    tags=['Admin']
)

app.include_router(
    events.router,
    prefix='/events',
    tags=["Events"]
)