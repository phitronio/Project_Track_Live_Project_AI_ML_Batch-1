from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.users.dependencies import CurrentUserDep, UserServiceDep
from app.modules.users.schemas import Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, service: UserServiceDep) -> UserRead:
    return await service.register(data)


@router.post("/login", response_model=Token)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], service: UserServiceDep
) -> Token:
    return await service.login(form.username, form.password)


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUserDep) -> UserRead:
    return UserRead.model_validate(user)
