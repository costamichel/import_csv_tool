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

## Reportar problemas
Abra uma issue no Github ou envie sugestões para o autor.

## Licença
MIT
