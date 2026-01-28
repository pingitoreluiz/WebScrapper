import sqlite3
import os
import csv
import json
from datetime import datetime

# Caminho absoluto para a pasta data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DB_NAME = os.path.join(DATA_DIR, "prices.db")


def get_connection():
    """Cria uma conexão com o arquivo do banco de dados."""
    return sqlite3.connect(DB_NAME)


def create_table():
    """
    Cria a tabela 'prices' se ela ainda não existir.
    Também cria índices para melhorar performance de queries.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Cria tabela principal
    sql_command = """
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT NOT NULL,
        preco_original TEXT,
        preco_numerico REAL NOT NULL,
        marca_chip TEXT,
        fabricante TEXT,
        modelo TEXT,
        link TEXT UNIQUE,
        data_coleta TEXT NOT NULL,
        loja TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    cursor.execute(sql_command)

    # Cria índices para queries rápidas
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_loja ON prices(loja)",
        "CREATE INDEX IF NOT EXISTS idx_marca_chip ON prices(marca_chip)",
        "CREATE INDEX IF NOT EXISTS idx_fabricante ON prices(fabricante)",
        "CREATE INDEX IF NOT EXISTS idx_modelo ON prices(modelo)",
        "CREATE INDEX IF NOT EXISTS idx_preco ON prices(preco_numerico)",
        "CREATE INDEX IF NOT EXISTS idx_data_coleta ON prices(data_coleta)",
        "CREATE INDEX IF NOT EXISTS idx_link ON prices(link)",
    ]

    for index_sql in indices:
        cursor.execute(index_sql)

    conn.commit()
    conn.close()
    print("[OK] Tabela 'prices' e indices criados/verificados com sucesso.")


def save_price(data_dict):
    """
    Salva um único produto no banco de dados.
    Usa INSERT OR REPLACE para evitar duplicatas baseado no link.

    Args:
        data_dict: Dicionário com dados do produto

    Returns:
        Boolean indicando sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()

    # SQL com INSERT OR REPLACE para evitar duplicatas
    sql_command = """
    INSERT OR REPLACE INTO prices (
        produto, preco_original, preco_numerico, marca_chip, 
        fabricante, modelo, link, data_coleta, loja
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = (
        data_dict.get("Produto"),
        data_dict.get("Preco_Original"),
        data_dict.get("Preco_Numerico"),
        data_dict.get("Marca_Chip"),
        data_dict.get("Fabricante"),
        data_dict.get("Modelo"),
        data_dict.get("Link"),
        data_dict.get("Data_Coleta"),
        data_dict.get("Loja", "Desconhecida"),
    )

    try:
        cursor.execute(sql_command, values)
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")
        return False
    finally:
        conn.close()


def get_stats():
    """
    Retorna estatísticas do banco de dados

    Returns:
        Dicionário com estatísticas
    """
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    # Total de produtos
    cursor.execute("SELECT COUNT(*) FROM prices")
    stats["total_produtos"] = cursor.fetchone()[0]

    # Produtos por loja
    cursor.execute("SELECT loja, COUNT(*) FROM prices GROUP BY loja")
    stats["por_loja"] = dict(cursor.fetchall())

    # Produtos por marca de chip
    cursor.execute("SELECT marca_chip, COUNT(*) FROM prices GROUP BY marca_chip")
    stats["por_chip"] = dict(cursor.fetchall())

    # Preço médio
    cursor.execute("SELECT AVG(preco_numerico) FROM prices WHERE preco_numerico > 0")
    avg_price = cursor.fetchone()[0]
    stats["preco_medio"] = f"R$ {avg_price:.2f}" if avg_price else "N/A"

    # Preço mínimo e máximo
    cursor.execute(
        "SELECT MIN(preco_numerico), MAX(preco_numerico) FROM prices WHERE preco_numerico > 0"
    )
    min_price, max_price = cursor.fetchone()
    stats["preco_minimo"] = f"R$ {min_price:.2f}" if min_price else "N/A"
    stats["preco_maximo"] = f"R$ {max_price:.2f}" if max_price else "N/A"

    # Última coleta
    cursor.execute("SELECT MAX(data_coleta) FROM prices")
    stats["ultima_coleta"] = cursor.fetchone()[0] or "N/A"

    conn.close()
    return stats


def export_to_csv(output_file=None):
    """
    Exporta dados do banco para CSV

    Args:
        output_file: Caminho do arquivo de saída (opcional)

    Returns:
        Caminho do arquivo gerado
    """
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(DATA_DIR, f"export_{timestamp}.csv")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM prices ORDER BY loja, preco_numerico")
    rows = cursor.fetchall()

    # Pega nomes das colunas
    column_names = [description[0] for description in cursor.description]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        writer.writerows(rows)

    conn.close()
    print(f"✅ Dados exportados para: {output_file}")
    return output_file


def export_to_json(output_file=None):
    """
    Exporta dados do banco para JSON

    Args:
        output_file: Caminho do arquivo de saída (opcional)

    Returns:
        Caminho do arquivo gerado
    """
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(DATA_DIR, f"export_{timestamp}.json")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM prices ORDER BY loja, preco_numerico")
    rows = cursor.fetchall()

    # Pega nomes das colunas
    column_names = [description[0] for description in cursor.description]

    # Converte para lista de dicionários
    data = []
    for row in rows:
        data.append(dict(zip(column_names, row)))

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    conn.close()
    print(f"✅ Dados exportados para: {output_file}")
    return output_file


def get_best_prices(limit=10, chip_brand=None):
    """
    Retorna os melhores preços

    Args:
        limit: Número de resultados
        chip_brand: Filtrar por marca de chip (NVIDIA, AMD, INTEL)

    Returns:
        Lista de tuplas com dados dos produtos
    """
    conn = get_connection()
    cursor = conn.cursor()

    if chip_brand:
        sql = """
        SELECT produto, preco_numerico, loja, link, modelo
        FROM prices 
        WHERE marca_chip = ? AND preco_numerico > 0
        ORDER BY preco_numerico ASC
        LIMIT ?
        """
        cursor.execute(sql, (chip_brand, limit))
    else:
        sql = """
        SELECT produto, preco_numerico, loja, link, modelo
        FROM prices 
        WHERE preco_numerico > 0
        ORDER BY preco_numerico ASC
        LIMIT ?
        """
        cursor.execute(sql, (limit,))

    results = cursor.fetchall()
    conn.close()
    return results


def search_products(query, limit=20):
    """
    Busca produtos por termo

    Args:
        query: Termo de busca
        limit: Número máximo de resultados

    Returns:
        Lista de tuplas com dados dos produtos
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    SELECT produto, preco_numerico, loja, link, modelo, fabricante
    FROM prices 
    WHERE produto LIKE ? OR modelo LIKE ? OR fabricante LIKE ?
    ORDER BY preco_numerico ASC
    LIMIT ?
    """

    search_term = f"%{query}%"
    cursor.execute(sql, (search_term, search_term, search_term, limit))

    results = cursor.fetchall()
    conn.close()
    return results


def clear_old_data(days=30):
    """
    Remove dados antigos do banco

    Args:
        days: Número de dias para manter

    Returns:
        Número de registros removidos
    """
    conn = get_connection()
    cursor = conn.cursor()

    # SQLite não tem função DATE_SUB, então usamos data como string
    from datetime import timedelta

    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    cursor.execute("SELECT COUNT(*) FROM prices WHERE data_coleta < ?", (cutoff_date,))
    count = cursor.fetchone()[0]

    cursor.execute("DELETE FROM prices WHERE data_coleta < ?", (cutoff_date,))
    conn.commit()
    conn.close()

    print(f"[CLEANUP] Removidos {count} registros antigos (>{days} dias)")
    return count


if __name__ == "__main__":
    # Teste rápido se rodar este arquivo direto
    create_table()
    print("\n📊 Estatísticas do Banco:")
    stats = get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
