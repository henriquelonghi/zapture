import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Customer, Order, OrderItem, Product


@dataclass
class NormalizationSummary:
    orders_created: int = 0
    orders_updated: int = 0
    items_created: int = 0


def _get_or_create_product(
    db: Session, client_id: uuid.UUID, name: str, sku: str | None, category: str | None
) -> Product:
    query = db.query(Product).filter(Product.client_id == client_id)

    product = None
    if sku:
        product = query.filter(Product.sku == sku).first()
    elif name:
        product = query.filter(Product.sku.is_(None), Product.name == name).first()

    if product is None:
        product = Product(client_id=client_id, sku=sku, name=name, category=category)
        db.add(product)
        db.flush()
    elif category and not product.category:
        product.category = category

    return product


def _get_or_create_customer(db: Session, client_id: uuid.UUID, external_customer_id: str) -> Customer:
    customer = (
        db.query(Customer)
        .filter(Customer.client_id == client_id, Customer.external_customer_id == external_customer_id)
        .first()
    )
    if customer is None:
        customer = Customer(client_id=client_id, external_customer_id=external_customer_id)
        db.add(customer)
        db.flush()
    return customer


def _resolve_unit_cost(product: Product, row_unit_cost: float | None) -> float | None:
    """Ordem de prioridade: custo na própria linha > custo cadastrado manualmente > indisponível."""
    if row_unit_cost is not None:
        return row_unit_cost
    if product.costs:
        latest = sorted(product.costs, key=lambda c: c.updated_at)[-1]
        return float(latest.unit_cost)
    return None


def normalize_and_persist(
    db: Session,
    client_id: uuid.UUID,
    valid_rows: list[dict],
) -> NormalizationSummary:
    """Recebe linhas já validadas por schema_validator.validate_rows e persiste como
    Order/OrderItem/Product/Customer normalizados. Reingestão do mesmo pedido_id
    substitui os itens anteriores (idempotente por pedido)."""

    summary = NormalizationSummary()
    orders_by_external_id: dict[str, Order] = {}

    for row in valid_rows:
        external_order_id = row["pedido_id"]
        order = orders_by_external_id.get(external_order_id)

        if order is None:
            order = (
                db.query(Order)
                .filter(Order.client_id == client_id, Order.external_order_id == external_order_id)
                .first()
            )
            is_new = order is None
            if order is None:
                order = Order(client_id=client_id, external_order_id=external_order_id, order_date=row["data_pedido"])
            else:
                order.order_date = row["data_pedido"]

            if row["cliente_id"]:
                customer = _get_or_create_customer(db, client_id, row["cliente_id"])
                order.customer_id = customer.id

            db.add(order)
            db.flush()
            orders_by_external_id[external_order_id] = order

            if is_new:
                summary.orders_created += 1
            else:
                summary.orders_updated += 1
                for existing_item in list(order.items):
                    db.delete(existing_item)
                db.flush()

        product = _get_or_create_product(db, client_id, row["produto"], row["sku"], row["categoria"])
        unit_cost = _resolve_unit_cost(product, row["custo_unitario"])

        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=row["produto"],
            sku=row["sku"],
            category=row["categoria"] or product.category,
            quantity=row["quantidade"],
            unit_price=row["valor_unitario"],
            total_price=row["valor_total"],
            unit_cost=unit_cost,
        )
        db.add(item)
        summary.items_created += 1

    db.commit()
    return summary
