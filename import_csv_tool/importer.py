import psycopg2
import pandas as pd
import re

class Importer:
    def __init__(self, params):
        self.params = params
        self.conn = None

    def _connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(
                host=self.params["host"],
                port=self.params["port"],
                user=self.params["user"],
                password=self.params["password"],
                dbname=self.params["dbname"]
            )

    def import_csv(self, filepath, filename):
        self._connect()
        try:
            df = pd.read_csv(filepath, sep=self.params["separator"], encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, sep=self.params["separator"], encoding="latin1")
        # Normalizar nome da tabela
        table_name = self._normalize_name(filename, self.params["prefix"])
        # Normalizar nomes das colunas
        df.columns = [self._normalize_name(col) for col in df.columns]
        cur = self.conn.cursor()
        if self.params["overwrite"]:
            cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        # Criar tabela
        create_table_sql = self._generate_create_table_sql(table_name, df)
        cur.execute(create_table_sql)
        # Inserir dados
        for _, row in df.iterrows():
            cols = ','.join(df.columns)
            vals = ','.join([self._format_value(v) for v in row])
            cur.execute(f"INSERT INTO {table_name} ({cols}) VALUES ({vals});")
        self.conn.commit()
        cur.close()

    def _normalize_name(self, name, prefix=None):
        # Substitui espaços, parênteses, barras, hífen e outros caracteres não alfanuméricos por underline
        name = re.sub(r'[^a-zA-Z0-9]', '_', name)
        name = name.lower()
        name = re.sub(r'\.csv$', '', name)
        # Remove underlines duplicados
        name = re.sub(r'_+', '_', name)
        # Remove underlines do início/fim
        name = name.strip('_')
        # Se começar com número, prefixa com 'col_'
        if re.match(r'^\d', name):
            name = f'col_{name}'
        if prefix:
            name = f"{prefix}_{name}"
        return name

    def _generate_create_table_sql(self, table_name, df):
        cols = []
        for col in df.columns:
            # Simples: tudo como TEXT
            cols.append(f"{col} TEXT")
        cols_sql = ', '.join(cols)
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_sql});"

    def _format_value(self, v):
        if pd.isna(v):
            return "NULL"
        return f"'{str(v).replace("'", "''")}'"
