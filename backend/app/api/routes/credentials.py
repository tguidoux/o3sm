import uuid
from typing import Any

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Credential,
    CredentialPrivate,
    CredentialPublic,
    CredentialsPublic,
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
def create_credential(*, session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Create new credential.
    """

    return crud.create_credential(session=session, owner=current_user)


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
