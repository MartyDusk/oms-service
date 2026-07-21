import pytest
from app.db import Base, engine, SessionLocal
from app.models import Sucursal, OrdenExterna, DetalleOrdenExterna
from app.services import OMSService, ReporteAnalíticoService


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_ingesta_y_rollback():
    payload = {
        "ordenes": [
            {
                "sucursal_id": 1,
                "total": 100,
                "detalles": [{"producto_id": 1, "cantidad": 2, "precio_unitario": 50}]
            },
            {
                "sucursal_id": 1,
                "total": 200,
                "detalles": [{"producto_id": 2, "cantidad": 4, "precio_unitario": 50}]
            },
            {
                "sucursal_id": 2,
                "total": 300,
                "detalles": [{"producto_id": 3, "cantidad": 6, "precio_unitario": 50}]
            },
            {
                "sucursal_id": 2,
                "total": 400,
                "detalles": [{"producto_id": 4, "cantidad": None, "precio_unitario": -100}]
            }
        ]
    }

    OMSService.recibir_lote_ordenes(payload)

    session = SessionLocal()
    try:
        assert session.query(Sucursal).count() == 0
        assert session.query(OrdenExterna).count() == 0
        assert session.query(DetalleOrdenExterna).count() == 0
    finally:
        session.close()


def test_exactitud_analitica():
    session = SessionLocal()
    try:
        suc = Sucursal(id=10, nombre="Sucursal 10")
        session.add(suc)
        session.flush()

        totals = []
        for i in range(20):
            total = 100 + i
            totals.append(total)
            orden = OrdenExterna(sucursal_id=10, total=total)
            session.add(orden)
        session.commit()

        resultado = ReporteAnalíticoService.ticket_promedio_por_sucursal(
            session)

        ticket = [x[1] for x in resultado if x[0] == 10][0]

        esperado = sum(totals) / len(totals)

        assert float(ticket) == esperado
    finally:
        session.close()
