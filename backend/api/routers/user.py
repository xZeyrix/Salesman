from typing import Annotated

from fastapi import APIRouter, Body
from backend.schemas.user import UserUpdate
from backend.api.deps import CurrentUserDep
from backend.core.database import DBSessionDep

router = APIRouter(prefix='/user', tags=['Пользователь'])

@router.get('/status')
async def get_wallet(user: CurrentUserDep) -> dict[str, str | None]:
    return {'status': user.status}

# @router.patch('/update')
# async def user_update(user: CurrentUserDep, 
#                       update_data: Annotated[UserUpdate, Body()],
#                       dbsession: DBSessionDep
#                       ) -> dict[str, str]:
