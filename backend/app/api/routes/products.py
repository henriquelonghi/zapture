"""Cadastro de custo/COGS por produto — pré-requisito pra margem sair de "sem
dado de custo" no relatório (app/engine/metrics/margin.py já lê
Product.costs; só faltava UI/endpoint pra preencher). Um cadastro por produto
substitui o anterior em vez de acumular histórico — normalizer.py já resolve
custo pelo mais recente (`updated_at`), então um único registro por produto é
suficiente pro motor funcionar."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_client, get_db
from app.models import Client, Product, ProductCost
from app.schemas.product import ProductCostIn, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


def _latest_cost(product: Product) -> float | None:
    if not product.costs:
        return None
    return float(sorted(product.costs, key=lambda c: c.updated_at)[-1].unit_cost)


def _to_out(product: Product) -> ProductOut:
    return ProductOut(id=product.id, sku=product.sku, name=product.name, category=product.category, unit_cost=_latest_cost(product))


@router.get("", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), client: Client = Depends(get_current_client)) -> list[ProductOut]:
    products = db.query(Product).filter(Product.client_id == client.id).order_by(Product.name).all()
    return [_to_out(p) for p in products]


@router.put("/{product_id}/cost", response_model=ProductOut)
def set_product_cost(
    product_id: uuid.UUID,
    payload: ProductCostIn,
    db: Session = Depends(get_db),
    client: Client = Depends(get_current_client),
) -> ProductOut:
    product = db.query(Product).filter(Product.id == product_id, Product.client_id == client.id).first()
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produto não encontrado.")

    if payload.unit_cost < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Custo não pode ser negativo.")

    cost = db.query(ProductCost).filter(ProductCost.product_id == product.id).first()
    if cost is None:
        cost = ProductCost(client_id=client.id, product_id=product.id, unit_cost=payload.unit_cost)
        db.add(cost)
    else:
        cost.unit_cost = payload.unit_cost
        cost.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(product)

    return _to_out(product)
