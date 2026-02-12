from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(LookupError)
    async def lookup_error_handler(request: Request, exc: LookupError):
        return JSONResponse(status_code=404, content={"detail": "resource not found"})

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"detail": "internal server error"})
