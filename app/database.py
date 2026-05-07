from sqlmodel import create_engine, Session
from sqlmodel import SQLModel
from .config import settings


engine = create_engine(settings.database_url, echo=False)


def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    SQLModel.metadata.create_all(engine)
