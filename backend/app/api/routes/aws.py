from typing import Any

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.api.routes.parameters import read_parameter
from app.models import Message
from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/")
@router.get("/")
@router.put("/")
@router.delete("/")
async def main_router(session: SessionDep, request: Request):
    # print("request", request, type(request))
    # print("headers", request.headers, type(request.headers))
    # body = await request.body()
    # json = await request.json()
    # print("body", body, type(body))
    # print("json", json, type(json))

    content_type: str | None = request.headers.get("content-type")
    x_amz_target: str | None = request.headers.get("x-amz-target")
    x_amz_date: str | None = request.headers.get("x-amz-date")
    authorization: str | None = request.headers.get("authorization")
    from app.models import User

    u = User(
        email="dawadw",
    )

    # TODO: Verify access key
    # TODO: Verify signature of the request
    # TODO: Retrieve the user of the access key
    # TODO: Switch to routes api calls in function of the target

    param = read_parameter(session, current_user=u, name="param2")
    return {"Parameter": param}
