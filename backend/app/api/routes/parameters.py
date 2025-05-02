import os
from typing import Any

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    ParameterCreate,
    ParameterPublic,
    ParametersPublic,
    ParameterUpdate,
)
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/", response_model=ParametersPublic)
def read_parameters(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    with_decryption: bool = False,
) -> Any:
    """
    Retrieve parameters.
    """

    print("with_decryption", with_decryption)

    parameters, count = crud.read_parameters(
        session,
        current_user,
        skip,
        limit,
        with_decryption=with_decryption,
        secret_key=os.environ.get(
            "O3SM_SECRET_KEY", "TkUTrhRhJ1-PRfIBiOA7OJrcSnxaMugEvdwAnyNXdCM="
        ),
    )

    return ParametersPublic(data=parameters, count=count)


@router.get("/{name}", response_model=ParameterPublic)
def read_parameter(
    session: SessionDep,
    current_user: CurrentUser,
    name: str,
    with_decryption: bool = False,
) -> Any:
    """
    Get parameter by name.
    """

    parameter = crud.get_parameter_by_name(
        session=session,
        name=name,
        secret_key=os.environ.get(
            "O3SM_SECRET_KEY", "TkUTrhRhJ1-PRfIBiOA7OJrcSnxaMugEvdwAnyNXdCM="
        ),
        with_decryption=with_decryption,
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
        secret_key=os.environ.get(
            "O3SM_SECRET_KEY", "TkUTrhRhJ1-PRfIBiOA7OJrcSnxaMugEvdwAnyNXdCM="
        ),
    )

    return parameter


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
    parameter = crud.update_parameter(
        session=session,
        current_user=current_user,
        name=name,
        parameter_in=parameter_in,
        O3SM_SECRET_KEY=os.environ.get(
            "O3SM_SECRET_KEY", "TkUTrhRhJ1-PRfIBiOA7OJrcSnxaMugEvdwAnyNXdCM="
        ),
    )
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
        secret_key=os.environ.get(
            "O3SM_SECRET_KEY", "TkUTrhRhJ1-PRfIBiOA7OJrcSnxaMugEvdwAnyNXdCM="
        ),
    )
    if not parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    if not current_user.is_superuser and (parameter.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(parameter)
    session.commit()
    return Message(message="Parameter deleted successfully")
