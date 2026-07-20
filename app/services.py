from sqlalchemy import func
from app.db import SessionLocal
from app.models import Sucursal, OrdenExterna, DetalleOrdenExterna


class OMSService:
    @staticmethod
    def recibir_lote_ordenes(payload_crudo):
        session = SessionLocal()
        try:
            for orden in payload_crudo["ordenes"]:
                if orden["total"] < 0:
                    raise ValueError("Total inválido")

                sucursal = session.query(Sucursal).filter_by(
                    id=orden["sucursal_id"]).first()
                if not sucursal:
                    sucursal = Sucursal(
                        id=orden["sucursal_id"], nombre=f"Sucursal {orden['sucursal_id']}")
                    session.add(sucursal)
                    session.flush()

                orden_db = OrdenExterna(
                    sucursal_id=orden["sucursal_id"],
                    total=orden["total"]
                )
                session.add(orden_db)
                session.flush()

                for detalle in orden["detalles"]:
                    if detalle["cantidad"] <= 0:
                        raise ValueError("Cantidad inválida")
                    if detalle["precio_unitario"] < 0:
                        raise ValueError("Precio inválido")

                    detalle_db = DetalleOrdenExterna(
                        orden_id=orden_db.id,
                        producto_id=detalle["producto_id"],
                        cantidad=detalle["cantidad"],
                        precio_unitario=detalle["precio_unitario"]
                    )
                    session.add(detalle_db)

            session.commit()
            return {"mensaje": "lote procesado correctamente"}

        except Exception as e:
            session.rollback()
            return {"error": str(e)}

        finally:
            session.close()


class ReporteAnaliticoService:
    @staticmethod
    def top_productos_vendidos(session):
        return (
            session.query(
                DetalleOrdenExterna.producto_id,
                func.sum(DetalleOrdenExterna.cantidad).label("total_vendido")
            )
            .group_by(DetalleOrdenExterna.producto_id)
            .order_by(func.sum(DetalleOrdenExterna.cantidad).desc())
            .limit(5)
            .all()
        )

    @staticmethod
    def ticket_promedio_por_sucursal(session):
        return (
            session.query(
                OrdenExterna.sucursal_id,
                func.avg(OrdenExterna.total).label("ticket_promedio")
            )
            .group_by(OrdenExterna.sucursal_id)
            .all()
        )
