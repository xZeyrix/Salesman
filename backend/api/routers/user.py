from typing import Annotated

from fastapi import APIRouter, Body
from backend.schemas.user import UserUpdate
from backend.api.deps import CurrentUserDep
from backend.core.database import DBSessionDep

router = APIRouter(prefix='/user', tags=['Пользователь'])

@router.get('/wallet')
async def get_wallet(user: CurrentUserDep) -> dict[str, str | None]:
    return {'wallet_key': user.wallet_key}

@router.patch('/update')
async def user_update(user: CurrentUserDep, 
                      update_data: Annotated[UserUpdate, Body(examples=[{'wallet_key': 'newapikeyfreedom'}])],
                      dbsession: DBSessionDep
                      ) -> dict[str, str]:
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(user, key, value)
    await dbsession.commit()
    return {'status': 'success', 'wallet_key': user.wallet_key}
