from abc import ABC, abstractmethod

from app.etl.metadata import update_last_synced
from sqlalchemy import text


class BasePipeline(ABC):

    def __init__(self, conn, last_sync):
        self.conn = conn
        self.last_sync = last_sync

    def run(self):
        self.execute()
        max_created_at = self.conn.execute(
            text(f"""
                SELECT MAX(created_at)
                FROM {self.source_table}
                WHERE :last_sync IS NULL
                   OR created_at > :last_sync
            """),
            {"last_sync": self.last_sync}
        ).scalar()
        if max_created_at is not None:
            update_last_synced(self.conn, self.pipeline_name, max_created_at)

    @property
    @abstractmethod
    def pipeline_name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def source_table(self):
        raise NotImplementedError

    @abstractmethod
    def execute(self):
        raise NotImplementedError
