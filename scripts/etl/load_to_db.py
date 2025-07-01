from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import load_dotenv
import os

# Carrega as variáveis do .env
load_dotenv()

# Usa a variável de ambiente
CONN_STRING = os.getenv("DB_CONN_STRING")

engine = create_engine(CONN_STRING)

# 3. CSVs processados
df_dim_cliente = pd.read_csv('data/processed/dim_cliente.csv')
df_dim_produto = pd.read_csv('data/processed/dim_produto.csv')
df_fato_vendas = pd.read_csv('data/processed/fato_vendas.csv')

# 5. Limpa a tabela dim_cliente (sem dropar tabela e sem afetar fks)
# Limpa a tabela dim_cliente
with engine.begin() as conn:
    conn.exec_driver_sql("DELETE FROM dim_cliente;")
    # ou, usando text():
    # conn.execute(text("DELETE FROM dim_cliente;"))
    print("🗑️  Conteúdo antigo de dim_cliente removido.")

# Insere o DataFrame na dim_cliente
df_dim_cliente.to_sql(
    'dim_cliente',
    engine,
    if_exists='append',
    index=False
)
print("✅ dim_cliente carregada com sucesso (append).")

# --- Dimensão Produto ---

# 1) Limpa o conteúdo antigo de dim_produto
with engine.begin() as conn:
    conn.exec_driver_sql("DELETE FROM dim_produto;")
    print("🗑️  Conteúdo antigo de dim_produto removido.")

# 2) Insere o DataFrame df_dim_produto
df_dim_produto.to_sql(
    'dim_produto',
    engine,
    if_exists='append',
    index=False
)
print("✅ dim_produto carregada com sucesso (append).")

# --- Fato Vendas ---