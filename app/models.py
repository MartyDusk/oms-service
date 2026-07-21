from db import Base as _Base
from typing import final as _final
from sqlalchemy.orm import relationship as _relationship
from sqlalchemy import Column as _Column, String as _String, Integer as _Integer, Numeric as _Numeric, ForeignKey as _ForeignKey


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
