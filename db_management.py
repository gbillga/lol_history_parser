import sqlite3
from utils import read_trusted_dataframe, SingletonMeta


class DB(metaclass=SingletonMeta):

    def __init__(self) -> None:
        connection = sqlite3.connect("data/rfd/lol_history.db")
        self.connection = connection

    def write_trd_df_to_rfd(self, dataset_name: str, table_name: str) -> int:
        df = read_trusted_dataframe(dataset_name)

        # Drop table if already exists
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        df.to_sql(name=table_name, con=self.connection)

        written_rows = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[
            0
        ]

        return written_rows
