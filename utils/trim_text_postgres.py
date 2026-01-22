#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aplicar TRIM() em todas as colunas de texto de tabelas PostgreSQL.

Este script conecta-se a um banco de dados PostgreSQL, identifica todas as colunas
de tipo texto (text, varchar, char, etc.) e aplica a função TRIM() para remover
espaços em branco no início e no final dos valores.

Autor: Michel Costa
"""

import psycopg2
from tqdm import tqdm
import sys

# ============================================================================
# CONFIGURAÇÕES - Preencha com os dados do seu banco PostgreSQL
# ============================================================================

# Configurações de conexão ao banco de dados PostgreSQL
DB_HOST = "localhost"          # Exemplo: "localhost" ou "192.168.1.100"
DB_PORT = 5433                # Porta padrão do PostgreSQL é 5432
DB_NAME = "lages_educacao_producao"          # Exemplo: "vendas_db"
DB_USER = "postgres"           # Exemplo: "postgres" ou "seu_usuario"
DB_PASSWORD = "postgres"      # Exemplo: "MinhaSenh@123"

# Prefixo das tabelas (opcional)
# Se definido (não None), apenas tabelas que começam com este prefixo serão processadas
# Exemplo: "tb_" processará apenas "tb_clientes", "tb_vendas", etc.
# Para processar todas as tabelas, defina como None
PREFIX = "cloud_"                  # Exemplo: "tb_" ou None para todas as tabelas

# ============================================================================
# CÓDIGO PRINCIPAL
# ============================================================================

def get_connection():
    """
    Estabelece e retorna uma conexão com o banco de dados PostgreSQL.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        sys.exit(1)


def get_text_columns(cursor, schema='public'):
    """
    Obtém todas as tabelas e suas colunas de tipo texto do schema especificado.
    
    Args:
        cursor: Cursor do banco de dados
        schema: Nome do schema (padrão: 'public')
    
    Returns:
        dict: Dicionário {table_name: [column_name1, column_name2, ...]}
    """
    query = """
        SELECT 
            t.table_name,
            c.column_name,
            c.data_type
        FROM 
            information_schema.tables t
        INNER JOIN 
            information_schema.columns c 
            ON t.table_name = c.table_name 
            AND t.table_schema = c.table_schema
        WHERE 
            t.table_schema = %s
            AND t.table_type = 'BASE TABLE'
            AND c.data_type IN ('character varying', 'character', 'text', 'varchar', 'char')
        ORDER BY 
            t.table_name, c.ordinal_position
    """
    
    cursor.execute(query, (schema,))
    results = cursor.fetchall()
    
    # Organizar os resultados em um dicionário
    tables_columns = {}
    for table_name, column_name, data_type in results:
        # Aplicar filtro de prefixo, se definido
        if PREFIX is not None and not table_name.startswith(PREFIX):
            continue
            
        if table_name not in tables_columns:
            tables_columns[table_name] = []
        tables_columns[table_name].append(column_name)
    
    return tables_columns


def apply_trim_to_column(cursor, table_name, column_name):
    """
    Aplica TRIM() a uma coluna específica de uma tabela.
    
    Args:
        cursor: Cursor do banco de dados
        table_name: Nome da tabela
        column_name: Nome da coluna
    """
    try:
        # Construir a query de UPDATE com TRIM
        query = f"""
            UPDATE "{table_name}"
            SET "{column_name}" = TRIM("{column_name}")
            WHERE "{column_name}" IS NOT NULL 
              AND "{column_name}" != TRIM("{column_name}")
        """
        
        cursor.execute(query)
        return cursor.rowcount
    except Exception as e:
        print(f"\n⚠️  Erro ao processar {table_name}.{column_name}: {e}")
        return 0


def main():
    """
    Função principal do script.
    """
    print("=" * 70)
    print("Script de TRIM em colunas de texto - PostgreSQL")
    print("=" * 70)
    print(f"Conectando ao banco: {DB_NAME}@{DB_HOST}:{DB_PORT}")
    print(f"Usuário: {DB_USER}")
    if PREFIX:
        print(f"Prefixo de tabelas: {PREFIX}")
    else:
        print("Processando TODAS as tabelas")
    print("=" * 70)
    print()
    
    # Conectar ao banco
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Obter todas as tabelas e colunas de texto
        print("🔍 Buscando tabelas e colunas de texto...")
        tables_columns = get_text_columns(cursor)
        
        if not tables_columns:
            print("⚠️  Nenhuma tabela encontrada com o prefixo especificado ou sem colunas de texto.")
            return
        
        # Contar total de colunas para a barra de progresso
        total_columns = sum(len(columns) for columns in tables_columns.values())
        
        print(f"✅ Encontradas {len(tables_columns)} tabela(s) com {total_columns} coluna(s) de texto.")
        print()
        
        # Confirmar antes de continuar
        response = input("Deseja continuar com a aplicação do TRIM? (s/n): ")
        if response.lower() != 's':
            print("❌ Operação cancelada pelo usuário.")
            return
        
        print()
        print("🚀 Iniciando processamento...")
        print()
        
        total_rows_updated = 0
        
        # Processar cada tabela e coluna com barra de progresso
        with tqdm(total=total_columns, desc="Progresso geral", unit="coluna") as pbar:
            for table_name, columns in tables_columns.items():
                for column_name in columns:
                    # Atualizar a descrição da barra de progresso
                    pbar.set_description(f"📝 {table_name}.{column_name}")
                    
                    # Aplicar TRIM
                    rows_updated = apply_trim_to_column(cursor, table_name, column_name)
                    total_rows_updated += rows_updated
                    
                    # Commit após cada coluna
                    conn.commit()
                    
                    # Atualizar a barra de progresso
                    pbar.update(1)
        
        print()
        print("=" * 70)
        print(f"✅ Processamento concluído!")
        print(f"Total de registros atualizados: {total_rows_updated}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Erro durante o processamento: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
