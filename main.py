from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from common.error import BadRequest, UnprocessableError
from config import Config
from database.mongo import connect_and_init_db, close_db_connect

from api.users import connect

app = FastAPI()

app.add_event_handler("startup", connect_and_init_db)
app.add_event_handler("shutdown", close_db_connect)

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


# API Path
app.include_router(
    connect.router,
    prefix='/users',
    tags=["users"]
)