import sqlite3
import csv
import os
from pathlib import Path
from datetime import datetime
import shutil

# Caminhos dos diretórios
BASE_DIR = Path(__file__).parent
BACKUP_DIR = BASE_DIR / 'backups'
DATA_DIR = BASE_DIR / 'data'
EXPORT_DIR = BASE_DIR / 'exports'
DB_PATH = DATA_DIR / 'livraria.db'

# Função para inicializar o banco de dados e criar a tabela se não existir
def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS livros (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT NOT NULL,
                        autor TEXT NOT NULL,
                        ano_publicacao INTEGER,
                        preco REAL)''')
    conn.commit()
    conn.close()

# CRUD Operations
def adicionar_livro(titulo, autor, ano_publicacao, preco):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)",
                   (titulo, autor, ano_publicacao, preco))
    conn.commit()
    conn.close()
    backup_db()

def exibir_livros():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    conn.close()
    return livros

def atualizar_preco(id_livro, novo_preco):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE livros SET preco = ? WHERE id = ?", (novo_preco, id_livro))
    conn.commit()
    conn.close()
    backup_db()

def remover_livro(id_livro):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM livros WHERE id = ?", (id_livro,))
    conn.commit()
    conn.close()
    backup_db()

def buscar_livros_por_autor(autor):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livros WHERE autor = ?", (autor,))
    livros = cursor.fetchall()
    conn.close()
    return livros

# Exportar para CSV
def exportar_para_csv():
    livros = exibir_livros()
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(EXPORT_DIR / 'livros_exportados.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
        writer.writerows(livros)

# Importar de CSV
def importar_de_csv(caminho_csv):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(caminho_csv, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Pular cabeçalho
        for row in reader:
            cursor.execute("INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)",
                           (row[1], row[2], int(row[3]), float(row[4])))
    conn.commit()
    conn.close()
    backup_db()

# Backup do banco de dados
def backup_db():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_file = BACKUP_DIR / f"backup_livraria_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.db"
    shutil.copy(DB_PATH, backup_file)
    limpar_backups()

# Limpeza de backups antigos (mantém apenas os 5 mais recentes)
def limpar_backups():
    backups = sorted(BACKUP_DIR.glob('*.db'), key=os.path.getmtime, reverse=True)
    if len(backups) > 5:
        for backup in backups[5:]:
            backup.unlink()

# Menu de opções
def menu():
    while True:
        print("\n1. Adicionar novo livro")
        print("2. Exibir todos os livros")
        print("3. Atualizar preço de um livro")
        print("4. Remover um livro")
        print("5. Buscar livros por autor")
        print("6. Exportar dados para CSV")
        print("7. Importar dados de CSV")
        print("8. Fazer backup do banco de dados")
        print("9. Sair")
        escolha = input("\nEscolha uma opção: ")

        if escolha == '1':
            titulo = input("Título: ")
            autor = input("Autor: ")
            ano_publicacao = int(input("Ano de Publicação: "))
            preco = float(input("Preço: "))
            adicionar_livro(titulo, autor, ano_publicacao, preco)
        elif escolha == '2':
            livros = exibir_livros()
            for livro in livros:
                print(livro)
        elif escolha == '3':
            id_livro = int(input("ID do livro: "))
            novo_preco = float(input("Novo preço: "))
            atualizar_preco(id_livro, novo_preco)
        elif escolha == '4':
            id_livro = int(input("ID do livro: "))
            remover_livro(id_livro)
        elif escolha == '5':
            autor = input("Autor: ")
            livros = buscar_livros_por_autor(autor)
            for livro in livros:
                print(livro)
        elif escolha == '6':
            exportar_para_csv()
        elif escolha == '7':
            caminho_csv = input("Caminho do arquivo CSV: ")
            importar_de_csv(caminho_csv)
        elif escolha == '8':
            backup_db()
        elif escolha == '9':
            break
        else:
            print("Opção inválida! Tente novamente.")

# Inicializar o sistema
if __name__ == "__main__":
    init_db()
    menu()
