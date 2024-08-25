import sqlite3

conexao = sqlite3.connect("medidas.db")
cursor = conexao.cursor()

cursor.execute('''
                CREATE TABLE IF NOT EXISTS USUARIOS (
                    usuario TEXT PRIMARY KEY,
                    nome TEXT,
                    senha TEXT
                )
            ''')

cursor.execute('''
                CREATE TABLE IF NOT EXISTS MEDIDAS (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT,
                    peso REAL,
                    ombro REAL,
                    peito REAL,
                    braco REAL,
                    antebraco REAL,
                    cintura REAL,
                    quadril REAL,
                    coxa REAL,
                    panturrilha REAL, 
                    usuario TEXT,
                    FOREIGN KEY (usuario) REFERENCES USUARIOS(usuario) ON DELETE CASCADE
                )       
            ''')

conexao.commit()
conexao.close()