import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

engine_local = create_engine(os.getenv('DB_CONN_STRING'))
engine_supabase = create_engine(os.getenv('DB_SUPABASE_CONN_STRING'))

df_dim_cliente = pd.read_csv('data/processed/dim_cliente.csv')
df_dim_produto = pd.read_csv('data/processed/dim_produto.csv')
df_fato_vendas = pd.read_csv('data/processed/fato_vendas.csv')


def carregar_banco(engine, nome_banco):
    with engine.begin() as conn:
        conn.execute(text('DELETE FROM fato_vendas;'))
        conn.execute(text('DELETE FROM dim_produto;'))
        conn.execute(text('DELETE FROM dim_cliente;'))

    df_dim_cliente.to_sql(
        'dim_cliente', engine, if_exists='append', index=False
    )

    df_dim_produto.to_sql(
        'dim_produto', engine, if_exists='append', index=False
    )

    df_fato_vendas.to_sql(
        'fato_vendas', engine, if_exists='append', index=False
    )

    print(f'✅ Carga concluída no {nome_banco}')


carregar_banco(engine_supabase, 'Supabase')
carregar_banco(engine_local, 'Postgres local')