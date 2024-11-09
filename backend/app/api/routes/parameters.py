import uuid
from typing import Any

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Parameter,
    ParameterCreate,
    ParameterPublic,
    ParametersPublic,
    ParameterUpdate,
)
from app.utils import get_date_timestamp
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter()


@router.get("/", response_model=ParametersPublic)
def read_parameters(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve parameters.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Parameter)
        count = session.exec(count_statement).one()
        statement = select(Parameter).offset(skip).limit(limit)
        parameters = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Parameter)
            .where(Parameter.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Parameter)
            .where(Parameter.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        parameters = session.exec(statement).all()

    return ParametersPublic(data=parameters, count=count)


@router.get("/{name}", response_model=ParameterPublic)
def read_parameter(
    session: SessionDep,
    current_user: CurrentUser,
    name: str,
) -> Any:
    """
    Get parameter by name.
    """
    parameter = crud.get_parameter_by_name(
        session=session,
        name=name,
    )
    if not parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    if not current_user.is_superuser and (parameter.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return parameter


@router.post("/", response_model=ParameterPublic)
def create_parameter(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    parameter_in: ParameterCreate,
) -> Any:
    """
    Create new parameter.
    """

    parameter = crud.create_parameter(
        session=session,
        parameter_in=parameter_in,
        owner=current_user,
    )

    return parameter


# Update is not needed for this project, so we will comment it out
@router.put("/{name}", response_model=ParameterPublic)
def update_parameter(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    name: str,
    parameter_in: ParameterUpdate,
) -> Any:
    """
    Update a parameter.
    """
    parameter = crud.get_parameter_by_name(
        session=session,
        name=name,
    )
    if not parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    if not current_user.is_superuser and (parameter.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = parameter_in.model_dump(exclude_unset=True)

    update_dict["LastModifiedDate"] = get_date_timestamp()

    # Make sure we don't update the name or arn as they are unique
    update_dict.pop("Name", None)
    update_dict.pop("ARN", None)

    parameter.sqlmodel_update(update_dict)
    session.add(parameter)
    session.commit()
    session.refresh(parameter)
    return parameter


@router.delete("/{name}")
def delete_parameter(
    session: SessionDep,
    current_user: CurrentUser,
    name: str,
) -> Message:
    """
    Delete a parameter.
    """
    parameter = crud.get_parameter_by_name(
        session=session,
        name=name,
    )
    if not parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    if not current_user.is_superuser and (parameter.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(parameter)
    session.commit()
    return Message(message="Parameter deleted successfully")
