import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from .importer import Importer

class ImportCSVToolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Import CSV Tool")
        self.geometry("800x600")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.import_tab = ImportTab(self.notebook)
        self.export_tab = ExportTab(self.notebook)
        self.notebook.add(self.import_tab, text="Importação")
        self.notebook.add(self.export_tab, text="Exportação")

def run_app():
    app = ImportCSVToolApp()
    app.mainloop()

class ImportTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.folder_path = tk.StringVar()
        self.db_host = tk.StringVar(value="localhost")
        self.db_port = tk.StringVar(value="5433")
        self.db_user = tk.StringVar(value="postgres")
        self.db_password = tk.StringVar(value="postgres")   # EXCLUIR VALOR PADRAO DEPOIS
        self.db_name = tk.StringVar(value="lagoasanta_livro")   # EXCLUIR VALOR PADRAO DEPOIS
        self.csv_separator = tk.StringVar(value=";")
        self.table_prefix = tk.StringVar(value="extracaofly")   # EXCLUIR VALOR PADRAO DEPOIS
        self.overwrite = tk.BooleanVar()
        self.csv_files = []
        self.selected_files = []
        self._build_ui()

    def _build_ui(self):
        # Pasta
        folder_frame = ttk.LabelFrame(self, text="Escolha a pasta com arquivos CSV")
        folder_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="Abrir", command=self._choose_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="Listar arquivos", command=self._list_csv_files).pack(side=tk.LEFT, padx=5)

        # Lista de arquivos
        self.files_frame = ttk.LabelFrame(self, text="Selecione os arquivos CSV para importar")
        self.files_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        # Botões selecionar/desmarcar todos acima da lista
        btn_frame = ttk.Frame(self.files_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(btn_frame, text="Selecionar todos", command=self._select_all_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Desmarcar todos", command=self._deselect_all_files).pack(side=tk.LEFT, padx=2)
        self.files_listbox = tk.Listbox(self.files_frame, selectmode=tk.MULTIPLE, height=10)
        self.files_listbox.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Parâmetros do banco
        db_frame = ttk.LabelFrame(self, text="Conexão com o banco de dados Postgres")
        db_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(db_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(db_frame, textvariable=self.db_host, width=20).grid(row=0, column=1, padx=5)
        ttk.Label(db_frame, text="Porta:").grid(row=0, column=2, sticky=tk.W, padx=5)
        ttk.Entry(db_frame, textvariable=self.db_port, width=6).grid(row=0, column=3, padx=5)
        ttk.Label(db_frame, text="Usuário:").grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Entry(db_frame, textvariable=self.db_user, width=20).grid(row=1, column=1, padx=5)
        ttk.Label(db_frame, text="Senha:").grid(row=1, column=2, sticky=tk.W, padx=5)
        ttk.Entry(db_frame, textvariable=self.db_password, show="*", width=20).grid(row=1, column=3, padx=5)
        ttk.Label(db_frame, text="Banco:").grid(row=2, column=0, sticky=tk.W, padx=5)
        ttk.Entry(db_frame, textvariable=self.db_name, width=20).grid(row=2, column=1, padx=5)

        # Parâmetros extras
        params_frame = ttk.LabelFrame(self, text="Parâmetros da importação")
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(params_frame, text="Separador do CSV:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(params_frame, textvariable=self.csv_separator, width=3).pack(side=tk.LEFT)
        ttk.Label(params_frame, text="Prefixo da tabela:").pack(side=tk.LEFT, padx=10)
        ttk.Entry(params_frame, textvariable=self.table_prefix, width=15).pack(side=tk.LEFT)
        ttk.Checkbutton(params_frame, text="Sobrescrever tabela se existir", variable=self.overwrite).pack(side=tk.LEFT, padx=10)

        # Botão de importação
        ttk.Button(self, text="Importar arquivos selecionados", command=self._import_selected_files).pack(pady=10)

    def _select_all_files(self):
        self.files_listbox.select_set(0, tk.END)

    def _deselect_all_files(self):
        self.files_listbox.select_clear(0, tk.END)

    def _choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def _list_csv_files(self):
        import os
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("Atenção", "Selecione uma pasta primeiro.")
            return
        self.csv_files = [f for f in os.listdir(folder) if f.lower().endswith('.csv')]
        self.files_listbox.delete(0, tk.END)
        for f in self.csv_files:
            self.files_listbox.insert(tk.END, f)

    def _import_selected_files(self):
        selected_indices = self.files_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Atenção", "Selecione ao menos um arquivo para importar.")
            return
        selected_files = [self.csv_files[i] for i in selected_indices]
        params = {
            "host": self.db_host.get(),
            "port": self.db_port.get(),
            "user": self.db_user.get(),
            "password": self.db_password.get(),
            "dbname": self.db_name.get(),
            "separator": self.csv_separator.get(),
            "prefix": self.table_prefix.get(),
            "overwrite": self.overwrite.get(),
        }
        folder = self.folder_path.get()
        importer = Importer(params)
        success = True
        for filename in selected_files:
            filepath = os.path.join(folder, filename)
            try:
                table_name = importer._normalize_name(filename, params["prefix"])
                importer.import_csv(filepath, filename)
            except Exception as e:
                success = False
                messagebox.showerror(
                    "Erro",
                    f"Erro ao importar arquivo '{filename}' para tabela '{table_name}':\n{str(e)}"
                )
        if success:
            messagebox.showinfo("Sucesso", "Arquivos importados com sucesso!")

class ExportTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Funcionalidade de exportação em breve.").pack(pady=20)
