from os import getenv as _env
from typing import final as _final, Protocol as _Protocol
from sqlalchemy import create_engine as _createEngine, Engine as _Engine
from sqlalchemy.orm import sessionmaker as _SessionMaker, declarative_base as _declarativeBase, Session as _Session


class IDatabaseInfo(_Protocol):
    @property
    def engine(self) -> _Engine: ...
    @property
    def declarativeBase(self) -> object: ...
    @property
    def localSession(self) -> _SessionMaker[_Session]: ...


@_final
class DatabaseInfo(IDatabaseInfo):
    def __init__(self, envURL: str) -> None:
        gotEnv = _env(envURL)
        if gotEnv is None:
            raise Exception(f'{envURL!r}')
        engine = _createEngine(gotEnv, pool_pre_ping=True)
        self.__engine = engine
        self.__declarativeBase = _declarativeBase()
        self.__localSession = _SessionMaker(
            bind=engine, autoflush=False, autocommit=False)

    @property
    def engine(self) -> _Engine:
        return self.__engine

    @property
    def localSession(self):
        return self.__localSession

    @property
    def declarativeBase(self):
        return self.__declarativeBase


# FIXME
x = DatabaseInfo('DATABASE_URL')
engine = x.engine
SessionLocal = x.localSession
Base = x.declarativeBase
