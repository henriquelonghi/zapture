from io import BytesIO

import pandas as pd

from app.ingestion.upload_source import UploadSource


def test_reads_csv_and_normalizes_headers():
    csv_content = "Data_Pedido,Pedido_ID,Produto,Quantidade,Valor_Unitario\n2026-07-01,P1,Produto A,1,10\n"
    source = UploadSource(BytesIO(csv_content.encode("utf-8")), "vendas.csv")

    rows = source.fetch_rows()

    assert rows == [
        {
            "data_pedido": "2026-07-01",
            "pedido_id": "P1",
            "produto": "Produto A",
            "quantidade": "1",
            "valor_unitario": "10",
        }
    ]


def test_reads_xlsx():
    df = pd.DataFrame(
        [
            {
                "Data_Pedido": "2026-07-01",
                "Pedido_ID": "P1",
                "Produto": "Produto A",
                "Quantidade": 1,
                "Valor_Unitario": 10,
            }
        ]
    )
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    source = UploadSource(buffer, "vendas.xlsx")
    rows = source.fetch_rows()

    assert rows[0]["pedido_id"] == "P1"
    assert rows[0]["produto"] == "Produto A"


def test_unsupported_extension_raises():
    try:
        UploadSource(BytesIO(b""), "vendas.txt").fetch_rows()
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass
