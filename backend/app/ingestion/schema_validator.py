"""Validação de schema dos dados de vendas (Sheets/CSV/XLSX).

Regra de ouro: nunca deixar erro silencioso gerar número furado. Colunas
obrigatórias ausentes bloqueiam a ingestão inteira; colunas recomendadas
ausentes viram avisos (o motor segue, mas com funcionalidade reduzida);
linhas com dados inválidos são excluídas individualmente, não descartam
o lote inteiro nem viram zero.
"""

from dataclasses import dataclass, field
from datetime import date, datetime

REQUIRED_COLUMNS = ["data_pedido", "pedido_id", "produto", "quantidade", "valor_unitario"]

RECOMMENDED_COLUMNS = {
    "sku": "margem por produto pode ficar imprecisa (não será possível casar com custo cadastrado por SKU)",
    "cliente_id": "a métrica 'clientes que sumiram' ficará indisponível",
    "custo_unitario": "margem por produto dependerá de custo cadastrado manualmente",
}

_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d")


@dataclass
class RowError:
    row_index: int
    message: str


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    row_errors: list[RowError] = field(default_factory=list)
    valid_rows: list[dict] = field(default_factory=list)


def _parse_date(value: object) -> date | None:
    if isinstance(value, date):
        return value
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _parse_number(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    if text.count(",") == 1 and text.count(".") == 0:
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def validate_rows(rows: list[dict[str, object]]) -> ValidationResult:
    result = ValidationResult(is_valid=True)

    if not rows:
        result.is_valid = False
        result.errors.append("Nenhuma linha encontrada na fonte de dados.")
        return result

    available_columns = {str(c).strip().lower() for c in rows[0]}

    missing_required = [c for c in REQUIRED_COLUMNS if c not in available_columns]
    if missing_required:
        result.is_valid = False
        result.errors.append("Colunas obrigatórias ausentes: " + ", ".join(missing_required))
        return result

    for col, warning_text in RECOMMENDED_COLUMNS.items():
        if col not in available_columns:
            result.warnings.append(f"Coluna '{col}' não encontrada — {warning_text}.")

    for idx, raw_row in enumerate(rows):
        row = {str(k).strip().lower(): v for k, v in raw_row.items()}

        order_date = _parse_date(row.get("data_pedido"))
        pedido_id = str(row.get("pedido_id") or "").strip()
        produto = str(row.get("produto") or "").strip()
        quantidade = _parse_number(row.get("quantidade"))
        valor_unitario = _parse_number(row.get("valor_unitario"))

        row_problems = []
        if order_date is None:
            row_problems.append("data_pedido inválida ou ausente")
        if not pedido_id:
            row_problems.append("pedido_id ausente")
        if not produto:
            row_problems.append("produto ausente")
        if quantidade is None or quantidade <= 0:
            row_problems.append("quantidade inválida")
        if valor_unitario is None or valor_unitario < 0:
            row_problems.append("valor_unitario inválido")

        if row_problems:
            result.row_errors.append(RowError(row_index=idx, message="; ".join(row_problems)))
            continue

        valor_total = _parse_number(row.get("valor_total"))
        if valor_total is None:
            valor_total = round(quantidade * valor_unitario, 2)

        result.valid_rows.append(
            {
                "data_pedido": order_date,
                "pedido_id": pedido_id,
                "produto": produto,
                "sku": str(row.get("sku") or "").strip() or None,
                "categoria": str(row.get("categoria") or "").strip() or None,
                "quantidade": quantidade,
                "valor_unitario": valor_unitario,
                "valor_total": valor_total,
                "cliente_id": str(row.get("cliente_id") or "").strip() or None,
                "custo_unitario": _parse_number(row.get("custo_unitario")),
            }
        )

    if not result.valid_rows:
        result.is_valid = False
        result.errors.append("Nenhuma linha válida após validação de dados.")

    return result
