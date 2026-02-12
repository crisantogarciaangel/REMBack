from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.api.v1.routes.health import router as health_router
from app.api.v1.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(title="KYC Onboarding API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
