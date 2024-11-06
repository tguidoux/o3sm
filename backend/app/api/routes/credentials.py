import uuid
from typing import Any

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Credential,
    CredentialCreate,
    CredentialPrivate,
    CredentialPublic,
    CredentialsPublic,
    CredentialUpdate,
    Message,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter()


@router.get("/", response_model=CredentialsPublic)
def read_credentials(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve credentials.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Credential)
        count = session.exec(count_statement).one()
        statement = select(Credential).offset(skip).limit(limit)
        credentials = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Credential)
            .where(Credential.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Credential)
            .where(Credential.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        credentials = session.exec(statement).all()

    return CredentialsPublic(data=credentials, count=count)


@router.get("/{id}", response_model=CredentialPublic)
def read_credential(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get credential by ID.
    """
    credential = session.get(Credential, id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    if not current_user.is_superuser and (credential.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return credential


@router.post("/", response_model=CredentialPrivate)
def create_credential(
    *, session: SessionDep, current_user: CurrentUser, credential_in: CredentialCreate
) -> Any:
    """
    Create new credential.
    """

    credential, secret_key = crud.create_credential(session=session, owner=current_user)
    # Change the return type to CredentialPrivate, this should be done only once while the credential is created
    credential.secret_key = secret_key
    return credential


# Update is not needed for this project, so we will comment it out
# @router.put("/{id}", response_model=CredentialPublic)
# def update_credential(
#     *,
#     session: SessionDep,
#     current_user: CurrentUser,
#     id: uuid.UUID,
#     credential_in: CredentialUpdate,
# ) -> Any:
#     """
#     Update an credential.
#     """
#     credential = session.get(Credential, id)
#     if not credential:
#         raise HTTPException(status_code=404, detail="Credential not found")
#     if not current_user.is_superuser and (credential.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     update_dict = credential_in.model_dump(exclude_unset=True)
#     credential.sqlmodel_update(update_dict)
#     session.add(credential)
#     session.commit()
#     session.refresh(credential)
#     return credential


@router.delete("/{id}")
def delete_credential(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an credential.
    """
    credential = session.get(Credential, id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    if not current_user.is_superuser and (credential.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(credential)
    session.commit()
    return Message(message="Credential deleted successfully")
