from typing import Any

from app import crud
from app.api.deps import SessionDep
from app.api.routes.parameters import (
    create_parameter,
    delete_parameter,
    read_parameter,
    read_parameters,
    update_parameter,
)
from app.core.aws_sigv4 import AWSSigV4Verifier, InvalidSignatureError
from app.models import (
    AWSParameterPublic,
    AWSParametersPublic,
    ParameterCreate,
    ParameterPublic,
    ParametersPublic,
    ParameterUpdate,
    User,
)
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


class AWSRequestsRouter(object):

    X_AMZ_TARGETS = {
        "AmazonSSM.GetParameter": "get_parameter",
        "AmazonSSM.DescribeParameters": "describe_parameters",
        "AmazonSSM.PutParameter": "put_parameter",
        "AmazonSSM.DeleteParameter": "delete_parameter",
    }

    def __init__(self, session: SessionDep, request: Request) -> None:
        self.session = session
        self.request = request

    async def get_parameter(self, owner: User) -> Any:
        body_json: dict = await self.request.json()  # type: ignore

        name: str | None = body_json.get("Name")
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")

        param: ParameterPublic = read_parameter(
            self.session, current_user=owner, name=name
        )
        return AWSParameterPublic(Parameter=param)

    async def describe_parameters(self, owner: User) -> Any:
        # body_json: dict = await self.request.json()  # type: ignore

        parameters: ParametersPublic = read_parameters(self.session, current_user=owner)
        return AWSParametersPublic(Parameters=parameters.data)

    async def put_parameter(self, owner: User) -> Any:
        body_json: dict = await self.request.json()  # type: ignore

        name: str | None = body_json.get("Name")  # type: ignore
        value: str | None = body_json.get("Value")
        type: str | None = body_json.get("Type")

        if not name:
            raise HTTPException(status_code=400, detail="Name is required")

        if not value:
            raise HTTPException(status_code=400, detail="Value is required")

        if not type:
            raise HTTPException(status_code=400, detail="Type is required")

        # Check if the parameter already exists
        parameter = crud.get_parameter_by_name(session=self.session, name=name)
        if parameter:
            # Create a ParameterUpdate object from parameter and body_json
            update_json = parameter.model_dump()
            update_json.update(body_json)
            parameter_update: ParameterUpdate = ParameterUpdate(**update_json)

            return update_parameter(
                session=self.session,
                current_user=owner,
                name=name,
                parameter_in=parameter_update,
            )
        else:
            parameter_create: ParameterCreate = ParameterCreate(**body_json)
            return create_parameter(
                session=self.session,
                current_user=owner,
                parameter_in=parameter_create,
            )

    async def delete_parameter(self, owner: User) -> Any:
        body_json: dict = await self.request.json()  # type: ignore

        name: str | None = body_json.get("Name")  # type: ignore
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")

        message = delete_parameter(self.session, current_user=owner, name=name)

        return message

    async def main_router(self) -> Any:
        method: str = self.request.method
        body = await self.request.body()
        headers_dict = dict(self.request.headers)

        # Currently only support SSM service
        # We can easily extend this to support other services

        # Verify the request signature and authorization
        verifier: AWSSigV4Verifier = AWSSigV4Verifier(
            request_method=method,
            uri_path="/",
            headers=headers_dict,
            body=body,
            service="ssm",
            timestamp_mismatch=None,
        )

        credential = crud.get_credential_by_access_key(
            session=self.session,
            access_key=verifier.access_key,
        )

        if not credential:
            raise HTTPException(status_code=404, detail="Access key not found")

        verifier.key_mapping = {credential.access_key: credential.secret_key}

        try:
            verifier.verify()
        except InvalidSignatureError as e:
            raise HTTPException(status_code=403, detail=str(e))

        # Retrieve the owner of the access key
        owner = credential.owner
        if not owner:
            raise HTTPException(status_code=404, detail="Owner not found")

        # Switch to routes api calls in function of the target
        x_amz_target = headers_dict.get("x-amz-target")
        if not x_amz_target:
            raise HTTPException(
                status_code=400, detail="x-amz-target header is required"
            )

        if x_amz_target not in self.X_AMZ_TARGETS:
            raise HTTPException(status_code=400, detail="Invalid x-amz-target header")

        # Call the method corresponding to the x_amz_target
        method_name = self.X_AMZ_TARGETS[x_amz_target]
        method = getattr(self, method_name)
        return await method(owner)


@router.post("/")
@router.get("/")
@router.put("/")
@router.delete("/")
async def main_router(session: SessionDep, request: Request) -> Any:
    aws_router = AWSRequestsRouter(session, request)
    return await aws_router.main_router()
