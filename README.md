# Import CSV Tool - v1.0 by Michel Costa

Ferramenta para importar arquivos CSV para o PostgreSQL ou exportar tabelas do banco para CSV.

## Funcionalidades
- Importação de múltiplos arquivos CSV para PostgreSQL
- Configuração de conexão, separador, prefixo, sobrescrever tabela
- Interface gráfica em Tkinter
- Exportação (em breve)


## Estrutura do Projeto
- `import_csv_tool/` - Código principal
- `tests/` - Testes automatizados
- `utils/` - Scripts utilitários independentes
  - `extract_oracle_bigtables/` - Script para extração de grandes tabelas Oracle em CSV
## Script de extração Oracle (independente)

Na pasta `utils/extract_oracle_bigtables` há um script chamado `extractor_oracle.py` para baixar grandes tabelas do Oracle em arquivos CSV divididos em chunks e juntar em um único arquivo final.

**Como usar:**
1. Edite o arquivo `extractor_oracle.py` e preencha as configurações de conexão e tabela com seus dados.
2. Instale a dependência do Oracle:
  ```bash
  pip install oracledb
  ```
3. Execute o script:
  ```bash
  python utils/extract_oracle_bigtables/extractor_oracle.py
  ```
4. Siga as instruções do script para juntar os arquivos em um único CSV final.

**Observação:**
Esse script é totalmente independente da ferramenta principal de importação/exportação de CSV para PostgreSQL.

## Requisitos
- Python 3.7+
- Instalar dependências:
  ```bash
  pip install -r requirements.txt
  ```


## Como usar

### Windows
Execute o arquivo `run_import_csv_tool.bat` na raiz do projeto para abrir a interface.

### Alternativamente
Execute:
```bash
python -m import_csv_tool
```

## Observações
- O programa tenta importar arquivos CSV usando UTF-8. Se houver erro de leitura, tenta automaticamente ISO-8859-1 (Latin-1).
- Nomes de tabelas e colunas são normalizados: espaços, hífens, parênteses, barras e caracteres especiais são convertidos para underline. Nomes que começam com número recebem prefixo `col_`.
- Todos os dados são importados como texto (TEXT) por padrão.


## Dependências
- [psycopg2-binary](https://pypi.org/project/psycopg2-binary/): conexão com PostgreSQL
- [pandas](https://pypi.org/project/pandas/): leitura de CSV
- [oracledb](https://pypi.org/project/oracledb/): (apenas para o script de extração Oracle)

## Reportar problemas
Abra uma issue no Github ou envie sugestões para o autor.

## Licença
MIT
