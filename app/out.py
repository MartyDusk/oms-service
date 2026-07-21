from logging import exception as _exception
from typing import final as _final, Protocol as _Protocol
from sqlalchemy.orm import Session as _Session, sessionmaker as _SessionMaker, declarative_base as _declarativeBase, relationship as _relationship
from sqlalchemy import Engine as _Engine, create_engine as _createEngine, func as _func
from os import getenv as _env
from sqlalchemy import Column as _Column, String as _String, Integer as _Integer, Numeric as _Numeric, ForeignKey as _ForeignKey
from out import Sucursal as _Sucursal, OrdenExterna as _OrdenExterna, DetalleOrdenExterna as _DetalleOrdenExterna


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
_engine = x.engine
_SessionLocal = x.localSession
_Base = x.declarativeBase


@_final
class Sucursal(_Base):
    __tablename__ = 'sucursal'

    id = _Column(_Integer, primary_key=True, index=True)
    nombre = _Column(_String(100), nullable=False)

    ordenes = _relationship('OrdenExterna', back_populates='sucursal')


@_final
class OrdenExterna(_Base):
    __tablename__ = 'orden_externa'

    id = _Column(_Integer, primary_key=True, autoincrement=True)
    sucursal_id = _Column(_Integer, _ForeignKey('sucursal.id'), nullable=False)
    total = _Column(_Numeric(12, 2), nullable=False)

    sucursal = _relationship('Sucursal', back_populates='ordenes')
    detalles = _relationship(
        'DetalleOrdenExterna', back_populates='orden', cascade='all, delete-orphan')


@_final
class DetalleOrdenExterna(_Base):
    __tablename__ = 'detalle_orden_externa'

    id = _Column(_Integer, primary_key=True, index=True)
    orden_id = _Column(_Integer, _ForeignKey(
        'orden_externa.id'), nullable=False)
    producto_id = _Column(_Integer, nullable=False)
    cantidad = _Column(_Integer, nullable=False)
    precio_unitario = _Column(_Numeric(12, 2), nullable=False)

    orden = _relationship('OrdenExterna', back_populates='detalles')


@_final
class OMSService:
    @staticmethod
    def recibir_lote_ordenes(payloadCrudo: dict[str, list[dict[str, object]]]) -> None:
        session = _SessionLocal()
        try:
            for orden in payloadCrudo['ordenes']:
                if orden['total'] < 0:  # type: ignore
                    raise ValueError('Total inválido')
                sucursal = session.query(_Sucursal).filter_by(
                    id=orden['sucursal_id']).first()
                if not sucursal:
                    sucursal = _Sucursal(
                        id=orden['sucursal_id'], nombre=f'Sucursal {orden['sucursal_id']}')
                    session.add(sucursal)
                    session.flush()
                orden_db = _OrdenExterna(
                    sucursal_id=orden['sucursal_id'],
                    total=orden['total']
                )
                session.add(orden_db)
                session.flush()
                for detalle in orden['detalles']:  # type: ignore
                    if detalle['cantidad'] <= 0:
                        raise ValueError('Cantidad inválida')
                    if detalle['precio_unitario'] < 0:
                        raise ValueError('Precio inválido')
                    detalle_db = _DetalleOrdenExterna(
                        orden_id=orden_db.id,
                        producto_id=detalle['producto_id'],
                        cantidad=detalle['cantidad'],
                        precio_unitario=detalle['precio_unitario']
                    )
                    session.add(detalle_db)
            session.commit()
        except BaseException as e:
            _exception(e)
            session.rollback()
        finally:
            session.close()


@_final
class ReporteAnalíticoService:
    @staticmethod
    def top_productos_vendidos(session: _Session):  # FIXME Missing type
        return (
            session.query(
                _DetalleOrdenExterna.producto_id,
                _func.sum(_DetalleOrdenExterna.cantidad).label('total_vendido')
            )
            .group_by(_DetalleOrdenExterna.producto_id)
            .order_by(_func.sum(_DetalleOrdenExterna.cantidad).desc())
            .limit(5)
            .all()
        )

    @staticmethod
    def ticket_promedio_por_sucursal(session: _Session):  # FIXME Missing type
        return (
            session.query(
                _OrdenExterna.sucursal_id,
                _func.avg(_OrdenExterna.total).label('ticket_promedio')
            )
            .group_by(_OrdenExterna.sucursal_id)
            .all()
        )
