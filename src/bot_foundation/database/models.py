from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()
BASEDIR = os.path.abspath(os.path.dirname(__file__))
engine = create_async_engine("sqlite+aiosqlite:///" + os.path.join(BASEDIR, 'data.db'))
AioSession = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base.metadata.bind = engine
AioSession.confifure(bind=engine)


class Blacklist(Base):
    __tablename__ = "blacklist"
    user_id = Column(BigInteger, primary_key=True, autoincrement=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
class Warn(Base):
    __tablename__ = "warn"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    server_id = Column(BigInteger, nullable=False)
    moderator_id = Column(BigInteger, nullable=False)
    reason = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    await engine.dispose()
    
    
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())
