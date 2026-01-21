"""
Script para substituir um caractere por outro em um arquivo.

Configuração:
- FILE_PATH: caminho do arquivo a ser processado
- OLD_CHAR: caractere a ser substituído
- NEW_CHAR: caractere substituto

O arquivo original será substituído pelo arquivo processado.
"""

import os
from tqdm import tqdm

# ==================== CONFIGURAÇÕES ====================
FILE_PATH = r"C:\Users\michel.costa\Desktop\Lagoa Santa - Livro\csv_extracao\20260121\Itens dos documentos fiscais das declaracoes.csv"  # Caminho do arquivo
OLD_CHAR = "¬"   # Caractere a ser substituído
NEW_CHAR = ";"   # Caractere substituto
# =======================================================


def replace_char_in_file(file_path, old_char, new_char):
    """
    Substitui um caractere por outro em um arquivo.
    
    Args:
        file_path (str): Caminho do arquivo
        old_char (str): Caractere a ser substituído
        new_char (str): Caractere substituto
    """
    if not os.path.exists(file_path):
        print(f"❌ Erro: Arquivo '{file_path}' não encontrado!")
        return
    
    if len(old_char) != 1 or len(new_char) != 1:
        print("❌ Erro: OLD_CHAR e NEW_CHAR devem ser caracteres únicos!")
        return
    
    print(f"📝 Processando arquivo: {file_path}")
    print(f"🔄 Substituindo '{old_char}' por '{new_char}'")
    
    # Obter tamanho do arquivo
    file_size = os.path.getsize(file_path)
    
    # Criar arquivo temporário
    temp_path = file_path + ".tmp"

    #encoding = 'utf-8'
    encoding = 'latin-1'  # Alternativa para arquivos com caracteres especiais
    
    try:
        # Ler e processar o arquivo com barra de progresso
        with open(file_path, 'r', encoding=encoding) as input_file, \
             open(temp_path, 'w', encoding=encoding) as output_file:
            
            # Barra de progresso baseada no tamanho do arquivo em bytes
            with tqdm(total=file_size, unit='B', unit_scale=True, desc="Progresso") as pbar:
                for line in input_file:
                    # Substituir caractere na linha
                    modified_line = line.replace(old_char, new_char)
                    output_file.write(modified_line)
                    
                    # Atualizar barra de progresso
                    pbar.update(len(line.encode('utf-8')))
        
        # Substituir arquivo original pelo temporário
        os.replace(temp_path, file_path)
        
        print(f"✅ Arquivo processado com sucesso!")
        print(f"📁 Arquivo salvo em: {file_path}")
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {str(e)}")
        # Remover arquivo temporário em caso de erro
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    replace_char_in_file(FILE_PATH, OLD_CHAR, NEW_CHAR)
