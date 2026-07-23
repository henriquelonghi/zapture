"""Leitura de dados via Google Sheets API.

O fluxo completo de OAuth (cliente autorizar acesso à própria planilha) entra
no onboarding, junto do relatório dinâmico (próxima etapa). Esta classe já
implementa a leitura em si, recebendo credenciais já resolvidas.
"""

from googleapiclient.discovery import build

from app.ingestion.base import IngestionSource


class SheetsSource(IngestionSource):
    label = "sheets"

    def __init__(self, spreadsheet_id: str, range_name: str, credentials):
        self._spreadsheet_id = spreadsheet_id
        self._range_name = range_name
        self._credentials = credentials

    def fetch_rows(self) -> list[dict[str, object]]:
        service = build("sheets", "v4", credentials=self._credentials)
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=self._spreadsheet_id, range=self._range_name)
            .execute()
        )
        values = result.get("values", [])
        if not values:
            return []

        header = [str(c).strip().lower() for c in values[0]]
        rows = []
        for raw_row in values[1:]:
            padded = raw_row + [""] * (len(header) - len(raw_row))
            rows.append(dict(zip(header, padded)))
        return rows
