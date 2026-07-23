from datetime import date

from app.ingestion.schema_validator import validate_rows


def test_missing_required_column_blocks_validation():
    rows = [{"data_pedido": "2026-07-01", "produto": "Produto A", "quantidade": "1", "valor_unitario": "10"}]

    result = validate_rows(rows)

    assert result.is_valid is False
    assert any("pedido_id" in e for e in result.errors)


def test_valid_rows_parsed_with_defaults():
    rows = [
        {
            "data_pedido": "01/07/2026",
            "pedido_id": "P1",
            "produto": "Produto A",
            "quantidade": "2",
            "valor_unitario": "10,50",
        }
    ]

    result = validate_rows(rows)

    assert result.is_valid is True
    assert len(result.valid_rows) == 1
    row = result.valid_rows[0]
    assert row["data_pedido"] == date(2026, 7, 1)
    assert row["valor_total"] == 21.0


def test_missing_recommended_column_generates_warning_not_error():
    rows = [
        {
            "data_pedido": "2026-07-01",
            "pedido_id": "P1",
            "produto": "Produto A",
            "quantidade": "1",
            "valor_unitario": "10",
        }
    ]

    result = validate_rows(rows)

    assert result.is_valid is True
    assert any("sku" in w for w in result.warnings)


def test_invalid_row_excluded_but_does_not_block_valid_rows():
    rows = [
        {
            "data_pedido": "2026-07-01",
            "pedido_id": "P1",
            "produto": "Produto A",
            "quantidade": "1",
            "valor_unitario": "10",
        },
        {
            "data_pedido": "",
            "pedido_id": "P2",
            "produto": "Produto B",
            "quantidade": "1",
            "valor_unitario": "10",
        },
    ]

    result = validate_rows(rows)

    assert result.is_valid is True
    assert len(result.valid_rows) == 1
    assert len(result.row_errors) == 1


def test_empty_source_is_invalid():
    result = validate_rows([])

    assert result.is_valid is False
