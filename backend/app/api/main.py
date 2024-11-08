from app.api.routes import credentials, login, parameters, users, utils
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(
    login.router,
    tags=["login"],
)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)
api_router.include_router(
    utils.router,
    prefix="/utils",
    tags=["utils"],
)
api_router.include_router(
    credentials.router,
    prefix="/credentials",
    tags=["credentials"],
)
api_router.include_router(
    parameters.router,
    prefix="/parameters",
    tags=["parameters"],
)
