from app.db import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric


class Sucursal(Base):
    __tablename__ = "sucursal"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)

    ordenes = relationship("OrdenExterna", back_populates="sucursal")


class OrdenExterna(Base):
    __tablename__ = "orden_externa"

    id = Column(Integer, primary_key=True, autoincrement =True)
    sucursal_id = Column(Integer, ForeignKey("sucursal.id"), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)

    sucursal = relationship("Sucursal", back_populates="ordenes")
    detalles = relationship(
        "DetalleOrdenExterna", back_populates="orden", cascade="all, delete-orphan")


class DetalleOrdenExterna(Base):
    __tablename__ = "detalle_orden_externa"

    id = Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer, ForeignKey("orden_externa.id"), nullable=False)
    producto_id = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)

    orden = relationship("OrdenExterna", back_populates="detalles")
