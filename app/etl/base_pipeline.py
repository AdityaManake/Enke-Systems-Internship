from abc import ABC, abstractmethod

from sqlalchemy import text
from types import NotImplementedType


class BasePipeline(ABC):
    pipeline_name: str = None

    def __init__(self, conn, last_sync, metadata):
        self.conn = conn
        self.last_sync = last_sync
        self.metadata = metadata

    def run(self):
        self.execute()
        self.validate()
        self.update_sync_time()

    def validate(self):
        _ = self.validate_pipeline

    def _max_created_at(self, table: str, column: str = "created_at"):
        """MAX(column) FROM table, restricted to rows newer than last_sync.

        Shared plumbing for update_sync_time() implementations - each pipeline
        still decides which table(s)/column(s) it calls this with, since that
        varies with what the pipeline actually joins on.
        """
        return self.conn.execute(
            text(f"""
                SELECT MAX({column})
                FROM {table}
                WHERE :last_sync IS NULL
                   OR {column} > :last_sync
            """),
            {"last_sync": self.last_sync}
        ).scalar()

    def _persist_sync_time(self, sync_time):
        if sync_time is not None:
            self.metadata.update_last_synced(self.conn, self.pipeline_name, sync_time)

    @staticmethod
    @abstractmethod
    def raw_query(where_clause: str = "") -> str:
        """Aggregation SELECT with an optional WHERE clause injection point.

        Single source of truth: execute() wraps it for the incremental
        materialization, and chart/perf code (app/queries) calls it directly
        against the raw tables, with no separate copy of the SQL.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self):
        raise NotImplementedError

    @abstractmethod
    def update_sync_time(self):
        """Persist last_sync for this pipeline's own source table(s).

        Each pipeline decides which table/column reflects its freshness -
        there is no single generic "source_table", since a pipeline can join
        several tables and only some of them matter for its incremental filter.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def validate_pipeline(self):
        raise NotImplementedError
