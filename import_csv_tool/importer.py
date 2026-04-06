import psycopg2
import pandas as pd
import re

reserved_words_replace = {
    "group": "group_", 
    "order": "order_",
    "select": "select_",
    "references": "references_",
}

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
        print(f"Lendo arquivo '{filename}'...")
        # Detecta tipo de arquivo e lê de acordo
        if filepath.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        else:
            try:
                df = pd.read_csv(filepath, sep=self.params["separator"], encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(filepath, sep=self.params["separator"], encoding="latin1")
        # Normalizar nome da tabela
        table_name = self._normalize_name(filename, self.params["prefix"], self.params.get("clean_prefix"))
        # Normalizar nomes das colunas
        df.columns = [self._normalize_name(col) for col in df.columns]
        cur = self.conn.cursor()
        # Verifica se a tabela existe
        cur.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);", (table_name,))
        exists = cur.fetchone()[0]
        if exists and not self.params["overwrite"]:
            print(f"Tabela '{table_name}' já existe. Importação ignorada para o arquivo '{filename}'.")
            cur.close()
            return  # Ignora importação se tabela existe e não deve sobrescrever
        if self.params["overwrite"]:
            print(f"Sobrescrevendo tabela '{table_name}' para o arquivo '{filename}'.")
            cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        print(f"Importando arquivo '{filename}' para tabela '{table_name}'...")
        # Criar tabela
        create_table_sql = self._generate_create_table_sql(table_name, df)
        try:
            cur.execute(create_table_sql)
        except Exception as e:
            print(create_table_sql)
            print(f"Erro ao criar tabela '{table_name}': {e}")
            cur.close()
            return
        # Inserir dados
        for _, row in df.iterrows():
            cols = ','.join(df.columns)
            vals = ','.join([self._format_value(v) for v in row])
            cur.execute(f"INSERT INTO {table_name} ({cols}) VALUES ({vals});")
        self.conn.commit()
        cur.close()
        print(f"Arquivo '{filename}' importado com sucesso para tabela '{table_name}'.")

    def _normalize_name(self, name, prefix=None, clean_prefix=None):
        # Remove extensão .csv, .xls, .xlsx primeiro
        name = re.sub(r'\.(csv|xls|xlsx)$', '', name, flags=re.IGNORECASE)
        # Remove prefixo inicial informado (case-insensitive), se houver
        if clean_prefix:
            pattern = re.compile(r'^' + re.escape(clean_prefix), flags=re.IGNORECASE)
            name = pattern.sub('', name)
        # Substitui espaços, parênteses, barras, hífen e outros caracteres não alfanuméricos por underline
        name = re.sub(r'[^a-zA-Z0-9]', '_', name)
        name = name.lower()
        # Remove underlines duplicados
        name = re.sub(r'_+', '_', name)
        # Remove underlines do início/fim
        name = name.strip('_')
        # Se começar com número, prefixa com 'col_'
        if re.match(r'^\d', name):
            name = f'col_{name}'
        if prefix:
            name = f"{prefix}_{name}"
        # Substitui palavras reservadas
        if name in reserved_words_replace:
            name = reserved_words_replace[name]
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
