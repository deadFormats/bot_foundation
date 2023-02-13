import os
from sqlalchemy.future import select

from bot_foundation.database import models


async def get_blacklisted_users() -> list:
    """
    This will return a list of all currently blacklisted users
    
    :return: List of records with user ids of blacklisted user
    """
    async with models.AioSession() as session:
        async with session.begin():
            result = await session.execute(
                select(models.Blacklist)
            )
            
            blacklist = result.scalars().all()
            return blacklist 
            
            

async def is_blacklisted(
