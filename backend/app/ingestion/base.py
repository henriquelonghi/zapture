from abc import ABC, abstractmethod


class IngestionSource(ABC):
    """Fonte de dados brutos (Google Sheets, upload de arquivo, etc)."""

    label: str

    @abstractmethod
    def fetch_rows(self) -> list[dict[str, object]]:
        """Retorna as linhas brutas como uma lista de dicts (chave = nome da coluna)."""
