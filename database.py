from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL="sqlite:///./social.db"

engine = create_engine(
    DATABASE_URL,connect_args={"check_same_thread":False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base: DeclarativeMeta = declarative_base()
Base.metadata.create_all(bind=engine)