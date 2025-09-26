# modules/utils.py
import pandas as pd
from pathlib import Path
import hashlib
from datetime import datetime

# BASE = Path.cwd()
# DB_DIR = BASE / "db"
# DB_DIR.mkdir(exist_ok=True)


# Caminho correto: dentro da pasta Fermon
BASE_DIR = Path(__file__).resolve().parent.parent  # Sobe 2 níveis até a raiz do projeto
DB_USERS = BASE_DIR / "db" / "users.xlsx"
DB_SALES = BASE_DIR / "db" / "sales.xlsx"
DB_STOCK = BASE_DIR / "db" / "stock.xlsx"

# Ensure default files with headers
def _ensure_file(path: Path, columns):
    if not path.exists():
        df = pd.DataFrame(columns=columns)
        df.to_excel(path, index=False)

# default headers
_ensure_file(DB_USERS, ["username", "password_hash", "role"])
_ensure_file(DB_STOCK, ["description", "balance", "cost", "price"])
_ensure_file(DB_SALES, [
    "data", "usuario", "produto", "quantidade",
    "preco", "tipo_pagamento", "valor_entregue", "total"
])

# ----- Users -----
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def load_users():
    df = pd.read_excel(DB_USERS)
    return df

def save_users(df):
    df.to_excel(DB_USERS, index=False)

def authenticate(username: str, password: str):
    df = load_users()
    if df.empty:
        # create default admin/admin if no users
        df = pd.DataFrame([{"username":"admin","password_hash":hash_pw("admin"),"role":"admin"}])
        save_users(df)
    row = df.loc[df["username"] == username]
    if not row.empty:
        pw_hash = row.iloc[0]["password_hash"]
        # handle plain passwords sometimes present (we expect hashed). If len not 64, try hash the stored plain text?
        if pw_hash == hash_pw(password):
            return {"username": username, "role": row.iloc[0]["role"]}
    return None

# ----- Stock -----
def load_items(path: Path = DB_STOCK):
    _ensure_file(path, ["description", "balance", "cost", "price"])
    df = pd.read_excel(path)
    # normalize columns if needed
    if "description" not in df.columns:
        df.columns = [c.lower().strip() for c in df.columns]
        # try to map common names
        mapping = {}
        for col in df.columns:
            if col in ("description","product","produto","item"):
                mapping[col] = "description"
            if col in ("balance","saldo","quantidade"):
                mapping[col] = "balance"
            if col in ("cost","custo"):
                mapping[col] = "cost"
            if col in ("price","preco"):
                mapping[col] = "price"
        df = df.rename(columns=mapping)
    # ensure types
    for c in ["balance","cost","price"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].fillna(0), errors="coerce").fillna(0)
    for c in ["description"]:
        if c not in df.columns:
            df[c] = ""
    return df[["description","balance","cost","price"]]

def save_items(df, path: Path = DB_STOCK):
    df.to_excel(path, index=False)

# ----- Sales -----
def load_sales(path: Path = DB_SALES):
    _ensure_file(path, ["data", "usuario", "tipo_pagamento", "produto", "quantidade", "preco"])
    df = pd.read_excel(path)
    return df

def save_sales(df, path: Path = DB_SALES):
    df.to_excel(path, index=False)

def append_sale(data, usuario, tipo_pagamento, produto, quantidade, preco, valor_entregue, path: Path = DB_SALES):
    """
    Adiciona uma nova venda com cabeçalho padronizado.
    Mantém compatibilidade com arquivos antigos (sem algumas colunas).
    """
    from datetime import datetime
    import numpy as np
    total = quantidade * preco

    # carrega e garante todas as colunas novas
    cols = ["data", "usuario", "tipo_pagamento", "produto", "quantidade",
             "preco", "valor_entregue", "total"]
    _ensure_file(path, cols)
    df = pd.read_excel(path)

    # garante presença das novas colunas mesmo em arquivos antigos
    for col in cols:
        if col not in df.columns:
            df[col] = np.nan

    nova = pd.DataFrame([{
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "usuario": usuario,
        "produto": produto,
        "quantidade": quantidade,
        "preco": preco,
        "tipo_pagamento": tipo_pagamento,
        "valor_entregue": valor_entregue,
        "total": total
    }])

    df = pd.concat([df[cols], nova], ignore_index=True)
    df.to_excel(path, index=False)

# ----- Configurações do App -----
CONFIG_FILE = BASE_DIR / "db" /"config.xlsx"

# garante que exista o arquivo com colunas padrão
def _ensure_config():
    if not CONFIG_FILE.exists():
        df = pd.DataFrame([{
            "banco": "Excel",       # Excel ou MySQL
            "caminho_db": str(BASE_DIR / "db" / "sales.xlsx"),
            "instituicao": "FERMAN",
            "impressora": ""
        }])
        df.to_excel(CONFIG_FILE, index=False)

_ensure_config()

def load_config() -> dict:
    """Carrega configuração como dicionário"""
    _ensure_config()
    try:
        df = pd.read_excel(CONFIG_FILE)
        return df.iloc[0].to_dict()
    except:
        return {}

def save_config(cfg: dict):
    """Salva as configurações fornecidas"""
    df = pd.DataFrame([cfg])
    df.to_excel(CONFIG_FILE, index=False)

def reset_stock():
    """Limpa o banco de dados de estoque"""
    stock_file = Path(DB_STOCK)
    if stock_file.exists():
        # cria DataFrame vazio com colunas padrão
        df = pd.DataFrame(columns=["description", "balance", "cost", "price"])
        df.to_excel(stock_file, index=False)

def reset_sales():
    """Limpa o banco de dados de vendas"""
    sales_file = Path(DB_SALES)
    if sales_file.exists():
        df = pd.DataFrame(columns=["data", "usuario", "tipo_pagamento", "produto", "quantidade", "preco", "valor_entregue", "total"])
        df.to_excel(sales_file, index=False)