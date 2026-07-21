from decimal import Decimal, InvalidOperation
from db import Base as _Base, engine, SessionLocal
from services import OMSService, ReporteAnalíticoService
from models import Sucursal as _Sucursal, OrdenExterna as _OrdenExterna

_Base.metadata.create_all(bind=engine)


def leer_int(msg: str) -> int:
    while True:
        try:
            return int(input(msg).strip())
        except ValueError:
            print("Ingresa un número entero válido.")


def leer_decimal(msg: str) -> Decimal:
    while True:
        try:
            return Decimal(input(msg).strip())
        except (InvalidOperation, ValueError):
            print("Ingresa un número decimal válido.")


def leer_str(msg: str) -> str:
    return input(msg).strip()


def pedir_detalles() -> list[dict[str, object]]:
    detalles = []
    n = leer_int("¿Cuántos detalles tendrá la orden? ")
    for i in range(1, n + 1):
        print(f"\nDetalle #{i}")
        producto_id = leer_int("  Producto ID: ")
        cantidad = leer_int("  Cantidad: ")
        precio_unitario = leer_decimal("  Precio unitario: ")
        detalles.append(
            {
                "producto_id": producto_id,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
            }
        )
    return detalles


def crear_orden_interactiva():
    print("\n=== Crear orden ===")
    sucursal_id = leer_int("Sucursal ID: ")
    total = leer_decimal("Total de la orden: ")
    detalles = pedir_detalles()
    payload = {
        "ordenes": [
            {
                "sucursal_id": sucursal_id,
                "total": total,
                "detalles": detalles,
            }
        ]
    }
    OMSService.recibir_lote_ordenes(payload)
    print("Orden enviada al sistema.")


def crear_lote_ordenes_interactivo():
    print("\n=== Crear lote de órdenes ===")
    n = leer_int("¿Cuántas órdenes deseas registrar? ")
    ordenes = []
    for i in range(1, n + 1):
        print(f"\nOrden #{i}")
        sucursal_id = leer_int("Sucursal ID: ")
        total = leer_decimal("Total de la orden: ")
        detalles = pedir_detalles()
        ordenes.append(
            {
                "sucursal_id": sucursal_id,
                "total": total,
                "detalles": detalles,
            }
        )
    OMSService.recibir_lote_ordenes({"ordenes": ordenes})
    print("Lote procesado.")


def mostrar_top_productos():
    print("\n=== Top productos vendidos ===")
    session = SessionLocal()
    try:
        resultados = ReporteAnalíticoService.top_productos_vendidos(session)
        if not resultados:
            print("Sin datos.")
            return
        for idx, (producto_id, total_vendido) in enumerate(resultados, start=1):
            print(f"{idx}. Producto {producto_id} -> {total_vendido}")
    finally:
        session.close()


def mostrar_ticket_promedio():
    print("\n=== Ticket promedio por sucursal ===")
    session = SessionLocal()
    try:
        resultados = ReporteAnalíticoService.ticket_promedio_por_sucursal(
            session)
        if not resultados:
            print("Sin datos.")
            return
        for sucursal_id, ticket_promedio in resultados:
            print(f"Sucursal {sucursal_id} -> {ticket_promedio}")
    finally:
        session.close()


def listar_sucursales():
    print("\n=== Sucursales ===")
    session = SessionLocal()
    try:
        sucursales = session.query(_Sucursal).order_by(_Sucursal.id).all()
        if not sucursales:
            print("Sin sucursales.")
            return
        for s in sucursales:
            print(f"ID: {s.id} | Nombre: {s.nombre}")
    finally:
        session.close()


def listar_ordenes():
    print("\n=== Órdenes ===")
    session = SessionLocal()
    try:
        ordenes = session.query(_OrdenExterna).order_by(_OrdenExterna.id).all()
        if not ordenes:
            print("Sin órdenes.")
            return
        for o in ordenes:
            print(f"ID: {o.id} | Sucursal: {o.sucursal_id} | Total: {o.total}")
    finally:
        session.close()


def menu_principal():
    while True:
        print("\n==============================")
        print("   DEMO / SHOWCASE DEL OMS")
        print("==============================")
        print("1. Crear orden")
        print("2. Crear lote de órdenes")
        print("3. Reportes")
        print("4. Consultas básicas")
        print("0. Salir")
        op = leer_str("Opción: ")
        if op == "1":
            crear_orden_interactiva()
        elif op == "2":
            crear_lote_ordenes_interactivo()
        elif op == "3":
            menu_reportes()
        elif op == "4":
            menu_consultas()
        elif op == "0":
            print("Hasta luego.")
            break
        else:
            print("Opción inválida.")


def menu_reportes():
    while True:
        print("\n--- Reportes ---")
        print("1. Top productos vendidos")
        print("2. Ticket promedio por sucursal")
        print("0. Volver")
        op = leer_str("Opción: ")
        if op == "1":
            mostrar_top_productos()
        elif op == "2":
            mostrar_ticket_promedio()
        elif op == "0":
            break
        else:
            print("Opción inválida.")


def menu_consultas():
    while True:
        print("\n--- Consultas básicas ---")
        print("1. Listar sucursales")
        print("2. Listar órdenes")
        print("0. Volver")
        op = leer_str("Opción: ")
        if op == "1":
            listar_sucursales()
        elif op == "2":
            listar_ordenes()
        elif op == "0":
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    menu_principal()
