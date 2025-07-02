from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import load_dotenv
import os

# Carrega as variáveis do .env
load_dotenv()
CONN_STRING = os.getenv("DB_CONN_STRING")
engine = create_engine(CONN_STRING)

# Lê os CSVs processados
df_dim_cliente = pd.read_csv('data/processed/dim_cliente.csv')
df_dim_produto = pd.read_csv('data/processed/dim_produto.csv')
df_fato_vendas = pd.read_csv('data/processed/fato_vendas.csv')

# --- 1) Limpa primeiro a fato_vendas
with engine.begin() as conn:
    conn.exec_driver_sql("DELETE FROM fato_vendas;")
    print("🗑️  Conteúdo antigo de fato_vendas removido.")

# --- 2) Depois limpa as dimensões (cliente e produto)
with engine.begin() as conn:
    conn.exec_driver_sql("DELETE FROM dim_produto;")
    print("🗑️  Conteúdo antigo de dim_produto removido.")

with engine.begin() as conn:
    conn.exec_driver_sql("DELETE FROM dim_cliente;")
    print("🗑️  Conteúdo antigo de dim_cliente removido.")

# --- 3) Insere primeiro as dimensões
df_dim_cliente.to_sql(
    'dim_cliente',
    engine,
    if_exists='append',
    index=False
)
print("✅ dim_cliente carregada com sucesso (append).")

df_dim_produto.to_sql(
    'dim_produto',
    engine,
    if_exists='append',
    index=False
)
print("✅ dim_produto carregada com sucesso (append).")

# --- 4) Por último insere a fato_vendas
df_fato_vendas.to_sql(
    'fato_vendas',
    engine,
    if_exists='append',
    index=False
)
print("✅ fato_vendas carregada com sucesso (append).")
