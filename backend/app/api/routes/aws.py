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
)
from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter()


@router.post("/")
@router.get("/")
@router.put("/")
@router.delete("/")
async def main_router(session: SessionDep, request: Request):

    method: str = request.method
    body = await request.body()
    headers_dict = dict(request.headers)

    # Currently only support SSM service
    # We can easily extend this to support other services

    # Verify the request signature and authorization
    verifier = AWSSigV4Verifier(
        request_method=method,
        uri_path="/",
        headers=headers_dict,
        body=body,
        service="ssm",
        timestamp_mismatch=None,
    )

    credential = crud.get_credential_by_access_key(
        session=session,
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
        raise HTTPException(status_code=400, detail="x-amz-target header is required")

    # TODO: Do a request switching on x_amz_target
    if x_amz_target == "AmazonSSM.GetParameter":
        # aws ssm get-parameter --name param2 --endpoint-url http://localhost:8000/ | cat
        body_json: dict = await request.json()  # type: ignore

        name: str | None = body_json.get("Name")  # type: ignore
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")

        param: ParameterPublic = read_parameter(session, current_user=owner, name=name)
        return AWSParameterPublic(Parameter=param)
    elif x_amz_target == "AmazonSSM.DescribeParameters":
        # aws ssm describe-parameters --endpoint-url http://localhost:8000/ --parameter-filters Key=param,Values=xxx,yyy | cat

        body_json: dict = await request.json()  # type: ignore

        # TODO: Implement parameter filters in read_parameters
        # parameter_filters: list[dict] | None = body_json.get("ParameterFilters")

        parameters: ParametersPublic = read_parameters(session, current_user=owner)
        return AWSParametersPublic(Parameters=parameters.data)
    elif x_amz_target == "AmazonSSM.PutParameter":
        # aws ssm put-parameter --endpoint-url http://localhost:8000/ --debug --name param3 --value "crazyvalue"
        body_json: dict = await request.json()  # type: ignore

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
        parameter = crud.get_parameter_by_name(session=session, name=name)
        if parameter:
            # Create a ParameterUpdate object from parameter and body_json
            update_json = parameter.model_dump()
            update_json.update(body_json)
            parameter_update: ParameterUpdate = ParameterUpdate(**update_json)

            return update_parameter(
                session=session,
                current_user=owner,
                name=name,
                parameter_in=parameter_update,
            )
        else:
            parameter_create: ParameterCreate = ParameterCreate(**body_json)
            return create_parameter(
                session=session,
                current_user=owner,
                parameter_in=parameter_create,
            )

    elif x_amz_target == "AmazonSSM.DeleteParameter":
        # aws ssm delete-parameter --name param3 --endpoint-url http://localhost:8000/ | cat
        body_json: dict = await request.json()  # type: ignore

        name: str | None = body_json.get("Name")  # type: ignore
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")

        message = delete_parameter(session, current_user=owner, name=name)
        return message

    else:
        raise HTTPException(status_code=400, detail="Invalid x-amz-target header")
