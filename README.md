# Import CSV Tool - v1.0 by Michel Costa

Ferramenta para importar arquivos CSV para o PostgreSQL ou exportar tabelas do banco para CSV.

## Funcionalidades
- Importação de múltiplos arquivos CSV e Excel (.xls, .xlsx) para PostgreSQL
- Configuração de conexão, separador (para CSV), prefixo, sobrescrever tabela
  - Campo adicional: "Limpeza de prefixo" remove um prefixo do nome do arquivo antes de criar a tabela (ex.: valor "CS_" transforma "CS_Aluno.csv" em tabela "aluno").
- Interface gráfica em Tkinter
- Exportação (em breve)


## Estrutura do Projeto
- `import_csv_tool/` - Código principal
- `tests/` - Testes automatizados
- `utils/` - Scripts utilitários independentes
  - `extract_oracle_bigtables/` - Script para extração de grandes tabelas Oracle em CSV
  - `replace_char.py` - Script para substituir caracteres em arquivos
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

## Script de substituição de caracteres (independente)

Na pasta `utils` há um script chamado `replace_char.py` para substituir um caractere por outro em arquivos.

**Como usar:**
1. Edite o arquivo `replace_char.py` e configure:
   - `FILE_PATH`: caminho do arquivo a ser processado
   - `OLD_CHAR`: caractere a ser substituído
   - `NEW_CHAR`: caractere substituto
2. Instale a dependência (caso ainda não tenha):
   ```bash
   pip install tqdm
   ```
3. Execute o script:
   ```bash
   python utils/replace_char.py
   ```
4. O script processará o arquivo com barra de progresso e substituirá o arquivo original.

**Observação:**
Esse script é totalmente independente da ferramenta principal de importação/exportação de CSV para PostgreSQL.

## Script de limpeza de espaços em branco no PostgreSQL (independente)

Na pasta `utils` há um script chamado `trim_text_postgres.py` para aplicar TRIM() em todas as colunas de tipo texto de tabelas PostgreSQL, removendo espaços em branco no início e fim dos valores.

**Como usar:**
1. Edite o arquivo `trim_text_postgres.py` e configure:
   - `DB_HOST`: endereço do servidor PostgreSQL (ex.: `"localhost"`)
   - `DB_PORT`: porta do PostgreSQL (ex.: `5432`)
   - `DB_NAME`: nome do banco de dados (ex.: `"vendas_db"`)
   - `DB_USER`: usuário do banco (ex.: `"postgres"`)
   - `DB_PASSWORD`: senha do usuário (ex.: `"MinhaSenh@123"`)
   - `PREFIX`: prefixo das tabelas a processar (ex.: `"tb_"` ou `None` para todas)
2. Instale as dependências (caso ainda não tenha):
   ```bash
   pip install psycopg2-binary tqdm
   ```
3. Execute o script:
   ```bash
   python utils/trim_text_postgres.py
   ```
4. O script mostrará quantas tabelas e colunas serão processadas e pedirá confirmação antes de continuar.
5. Durante a execução, uma barra de progresso mostrará qual tabela.coluna está sendo atualizada.

**Observação:**
Esse script é totalmente independente da ferramenta principal de importação/exportação de CSV para PostgreSQL. Ele apenas atualiza registros que possuem espaços em branco no início ou fim dos valores.

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
- Para arquivos CSV: o programa tenta importar usando UTF-8. Se houver erro de leitura, tenta automaticamente ISO-8859-1 (Latin-1).
- Para arquivos Excel (.xls, .xlsx): a leitura é feita diretamente pelo pandas, sem necessidade de configurar separador.
- Nomes de tabelas e colunas são normalizados: espaços, hífens, parênteses, barras e caracteres especiais são convertidos para underline. Nomes que começam com número recebem prefixo `col_`.
 - Se informado, o campo "Limpeza de prefixo" é aplicado ao início do nome do arquivo, removendo-o antes da normalização e antes do prefixo opcional ser adicionado.
- Todos os dados são importados como texto (TEXT) por padrão.


## Dependências
- [psycopg2-binary](https://pypi.org/project/psycopg2-binary/): conexão com PostgreSQL
- [pandas](https://pypi.org/project/pandas/): leitura de CSV e Excel
- [openpyxl](https://pypi.org/project/openpyxl/): leitura de arquivos Excel .xlsx
- [xlrd](https://pypi.org/project/xlrd/): leitura de arquivos Excel .xls
- [oracledb](https://pypi.org/project/oracledb/): (apenas para o script de extração Oracle)

## Reportar problemas
Abra uma issue no Github ou envie sugestões para o autor.

## Licença
MIT
