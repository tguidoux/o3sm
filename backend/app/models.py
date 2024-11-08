import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    credentials: list["Credential"] = Relationship(
        back_populates="owner", cascade_delete=True
    )
    parameters: list["Parameter"] = Relationship(
        back_populates="owner", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class CredentialBase(SQLModel):
    access_key: str = Field(max_length=255, index=True)
    secret_key: str = Field(max_length=255)


# Properties to receive on Credential creation
class CredentialCreate(SQLModel):
    pass


# Properties to receive on Credential update
# Cannot be updated
class CredentialUpdate(CredentialBase):
    pass


# Database model, database table inferred from class name
class Credential(CredentialBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="credentials")


# Properties to return via API, id is always required
class CredentialPublic(SQLModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    access_key: str


class CredentialPrivate(CredentialBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    access_key: str
    secret_key: str


class CredentialsPublic(SQLModel):
    data: list[CredentialPublic]
    count: int


class ParameterBase(SQLModel):
    name: str = Field(
        max_length=255,
        index=True,
        unique=True,
        primary_key=True,
        nullable=False,
    )
    value: str = Field(max_length=255, nullable=False)
    type: str = Field(max_length=255, default="string")
    version: int = Field(default=1)
    data_type: str = Field(max_length=255, default="text")


class ParameterCreate(ParameterBase):
    pass


class ParameterUpdate(ParameterBase):
    value: str
    type: str
    data_type: str


class Parameter(ParameterBase, table=True):
    last_modified_date: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )
    owner: User | None = Relationship(back_populates="parameters")


class ParameterPublic(ParameterBase):
    last_modified_date: str


class ParametersPublic(SQLModel):
    data: list[ParameterPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
