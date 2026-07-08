import os
from abc import ABC, abstractmethod
from enum import property

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import text


class BaseClass(ABC):
    def __init__(self, conn):
        self.conn = conn
        self.output_dir = os.path.join(self.queries_dir, "charts")
        self.queries_dir = os.path.dirname(os.path.abspath(__file__))

    def run(self):
        df = self.get_dataframe()
        df = self.normalize_columns(df)
        self.plot(df)
        self.save_charts()

    def run_query(self, file_name):
        with open(os.path.join(self.queries_dir, file_name)) as f:
            query = f.read()
        result = self.conn.execute(text(query))
        return pd.DataFrame(result.fetchall(), columns=result.keys())

    @property
    @abstractmethod
    def query_file(self):
        pass

    @property
    @abstractmethod
    def get_dataframe(self):
        pass

    def normalize_columns(self, df):
        return df

    @abstractmethod
    def plot(self, df):
        pass

    @property
    @abstractmethod
    def chart_name(self):
        pass

    def save_charts(self):
        os.makedirs(self.output_dir, exist_ok=True)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{self.chart_name}.png"))
        plt.close()
