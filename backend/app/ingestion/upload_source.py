from io import BytesIO
from pathlib import Path

import pandas as pd

from app.ingestion.base import IngestionSource


class UploadSource(IngestionSource):
    """Lê um arquivo CSV ou XLSX enviado pelo cliente (upload manual, sem sync automático)."""

    label = "upload"

    def __init__(self, file: bytes | BytesIO | str | Path, filename: str):
        self._file = file
        self._filename = filename

    def fetch_rows(self) -> list[dict[str, object]]:
        file = BytesIO(self._file) if isinstance(self._file, bytes) else self._file

        suffix = Path(self._filename).suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(file, dtype=str, keep_default_na=False)
        elif suffix in (".xlsx", ".xls"):
            df = pd.read_excel(file, dtype=str)
            df = df.fillna("")
        else:
            raise ValueError(f"Formato de arquivo não suportado: {suffix}")

        df.columns = [str(c).strip().lower() for c in df.columns]
        return df.to_dict(orient="records")
