import oracledb
import csv
csv.field_size_limit(100000000)
import os
import math


# --- INICIALIZAÇÃO DO CLIENTE ORACLE ---
# Força modo thin client (não usa Instant Client)
oracledb.init_oracle_client(lib_dir=None)
# ----------------------------------------



# --- CONFIGURAÇÕES ---
# Preencha com suas credenciais e informações do banco de dados
DB_HOST = "seu_host_oracle"  # Exemplo: "192.168.1.100"
DB_PORT = 1521  # Porta padrão Oracle é 1521
DB_USER = "seu_usuario"      # Exemplo: "USUARIO"
DB_PASSWORD = "sua_senha"    # Exemplo: "senha123"
DB_SID = "seu_sid"           # Exemplo: "orcl"
# Formato para SID via string TNS
DB_DSN = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={DB_HOST})(PORT={DB_PORT}))(CONNECT_DATA=(SID={DB_SID})))"
TABLE_NAME = "esquema.tabela" # Exemplo: "MEUESQUEMA.MINHATABELA"

# Parâmetros da extração
ID_MINIMO = 1
ID_MAXIMO = 1000000
TAMANHO_CHUNK = 30000

# Nomes dos arquivos de controle e saída
CONTROL_FILE = "controle_extracao.csv"
CHUNK_PREFIX = "chunk"
FINAL_FILE = "final.csv"
# --- FIM DAS CONFIGURAÇÕES ---

def gerar_arquivo_de_controle():
    """
    Cria o CSV de controle se ele não existir, calculando todos os ranges
    de IDs que precisam ser processados.
    """
    if os.path.exists(CONTROL_FILE):
        print(f"Arquivo de controle '{CONTROL_FILE}' já existe. Lendo status...")
        return

    print(f"Gerando novo arquivo de controle '{CONTROL_FILE}'...")
    
    header = ['chunk_num', 'id_inicio', 'id_fim', 'status', 'nome_arquivo']
    
    with open(CONTROL_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        chunk_num = 1
        id_atual = ID_MINIMO
        while id_atual <= ID_MAXIMO:
            id_inicio = id_atual
            id_fim = min(id_atual + TAMANHO_CHUNK - 1, ID_MAXIMO)
            nome_arquivo = f"{CHUNK_PREFIX}_{chunk_num}.csv"
            
            # Escreve a linha para este chunk
            writer.writerow([chunk_num, id_inicio, id_fim, 'pendente', nome_arquivo])
            
            # Prepara para o próximo chunk
            id_atual = id_fim + 1
            chunk_num += 1
    
    print("Arquivo de controle gerado com sucesso.")

def processar_chunks():
    """
    Lê o arquivo de controle e processa cada chunk marcado como 'pendente'.
    """
    # Garante que o arquivo de controle exista
    gerar_arquivo_de_controle()
    
    # Lê todas as tarefas do arquivo de controle para a memória
    tarefas = []
    with open(CONTROL_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tarefas.append(row)

    print("Iniciando conexão com o banco de dados Oracle...")
    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
            with connection.cursor() as cursor:
                print("Conexão bem-sucedida.")
                # Pega o nome das colunas da tabela para usar como cabeçalho
                cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE 1=0") # Query vazia para pegar metadados
                col_names = [row[0] for row in cursor.description]

                for i, tarefa in enumerate(tarefas):
                    if tarefa['status'] == 'pendente':
                        chunk_num = tarefa['chunk_num']
                        id_inicio = int(tarefa['id_inicio'])
                        id_fim = int(tarefa['id_fim'])
                        nome_arquivo = tarefa['nome_arquivo']

                        print(f"\n---> Processando Chunk {chunk_num}/{len(tarefas)}: IDs de {id_inicio} a {id_fim}")

                        try:
                            sql = f"SELECT * FROM {TABLE_NAME} WHERE id >= :start_id AND id <= :end_id"
                            cursor.execute(sql, start_id=id_inicio, end_id=id_fim)

                            with open(nome_arquivo, 'w', newline='', encoding='utf-8') as csvfile:
                                writer = csv.writer(csvfile)
                                # Escreve o cabeçalho
                                writer.writerow(col_names)
                                # Escreve as linhas de dados
                                for row in cursor:
                                    writer.writerow(row)

                            print(f"     Chunk {chunk_num} salvo com sucesso em '{nome_arquivo}'.")

                            # ATUALIZA O STATUS NA MEMÓRIA E REESCREVE O ARQUIVO DE CONTROLE
                            tarefas[i]['status'] = 'concluido'
                            with open(CONTROL_FILE, 'w', newline='', encoding='utf-8') as f_out:
                                writer = csv.DictWriter(f_out, fieldnames=tarefas[0].keys())
                                writer.writeheader()
                                writer.writerows(tarefas)

                        except oracledb.Error as e:
                            print(f"     ERRO no Oracle ao processar o chunk {chunk_num}: {e}")
                            print("     O script será interrompido. Você pode executá-lo novamente para continuar de onde parou.")
                            return # Interrompe a execução
                        except Exception as e:
                            print(f"     ERRO inesperado ao processar o chunk {chunk_num}: {e}")
                            return
    except oracledb.Error as e:
        print(f"Falha ao conectar ao banco de dados Oracle: {e}")
        return

    print("\nTodos os chunks foram processados com sucesso!")

def juntar_arquivos_chunk():
    """
    Junta todos os arquivos CSV de chunk em um único arquivo final.
    """
    print(f"\nIniciando a junção dos arquivos chunk em '{FINAL_FILE}'...")

    # Lê o arquivo de controle para saber quais arquivos juntar
    tarefas = []
    if not os.path.exists(CONTROL_FILE):
        print(f"ERRO: Arquivo de controle '{CONTROL_FILE}' não encontrado. Não é possível juntar os arquivos.")
        return
        
    with open(CONTROL_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Filtra apenas os que foram concluídos para evitar erros
        arquivos_chunks = [row['nome_arquivo'] for row in reader if row['status'] == 'concluido']

    if not arquivos_chunks:
        print("Nenhum chunk concluído para juntar.")
        return
        
    # Abre o arquivo final para escrita
    with open(FINAL_FILE, 'w', newline='', encoding='utf-8') as f_final:
        writer = csv.writer(f_final)
        
        # Processa o primeiro arquivo para pegar o cabeçalho
        primeiro_arquivo = arquivos_chunks[0]
        print(f"  Lendo {primeiro_arquivo} (com cabeçalho)...")
        with open(primeiro_arquivo, 'r', newline='', encoding='utf-8') as f_chunk:
            reader = csv.reader(f_chunk)
            # Escreve cabeçalho e todas as linhas no arquivo final
            for row in reader:
                writer.writerow(row)
        
        # Processa os arquivos restantes, pulando o cabeçalho
        for nome_arquivo in arquivos_chunks[1:]:
            print(f"  Lendo {nome_arquivo} (sem cabeçalho)...")
            with open(nome_arquivo, 'r', newline='', encoding='utf-8') as f_chunk:
                reader = csv.reader(f_chunk)
                next(reader) # Pula o cabeçalho
                for row in reader:
                    writer.writerow(row)

    print(f"\nArquivo '{FINAL_FILE}' criado com sucesso!")


if __name__ == "__main__":
    # Etapa 1: Processar e baixar todos os chunks
    processar_chunks()

    # Etapa 2: Perguntar ao usuário se deseja juntar os arquivos
    while True:
        resposta = input("\nDeseja juntar todos os arquivos de chunk em um único CSV final? (s/n): ").lower()
        if resposta in ['s', 'sim']:
            juntar_arquivos_chunk()
            break
        elif resposta in ['n', 'nao', 'não']:
            print("Operação de junção cancelada.")
            break
        else:
            print("Resposta inválida. Por favor, digite 's' para sim ou 'n' para não.")