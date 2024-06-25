# import libraries
import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
# import created database
from database.models import Base
# database settings
# DB_URL = postgressql+asyncpg: // login: password@localhost: 5432/db_name
# import functions wich create different info pages
from database.orm_query import orm_create_categories, orm_add_banner_description
# import text for database
from common.texts_for_db import categories, description_for_info_pages

# creating async engine
engine = create_async_engine(os.getenv('DB_URL'), echo=True)
# creating async session for working with database
session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False)


# function that starts database
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # creates sessions for different types of banners and categories
    async with session_maker() as session:
        await orm_create_categories(session, categories)
        await orm_add_banner_description(session, description_for_info_pages)


# function that drops database
async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
