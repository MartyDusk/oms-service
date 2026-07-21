from typing import final as _final
from sqlalchemy import func as _func
from logging import exception as _exception
from sqlalchemy.orm import Session as _Session
from db import SessionLocal as _SessionLocal
from models import Sucursal as _Sucursal, OrdenExterna as _OrdenExterna, DetalleOrdenExterna as _DetalleOrdenExterna


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
