import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from pathlib import Path

#conexao ao banco postgres local
env_path = Path(__file__).resolve().parents[1] / "scripts" / "etl" / ".env"
load_dotenv(env_path)
CONN_STRING = os.getenv("DB_CONN_STRING")
engine = create_engine(CONN_STRING)

#acesso as views no banco
df = pd.read_sql("SELECT * FROM vw_total_vendido_meio_pagamento", engine)
df["pagamento_nome"] = df["pagamento_nome"].replace("MercadoPago V1", "Mercado Pago")
df = df.groupby("pagamento_nome", as_index=False)["total_vendido"].sum()
df = df.sort_values("total_vendido", ascending=False)

df2 = pd.read_sql("SELECT * FROM vw_top_bairros_mais_clientes", engine)

df3 = pd.read_sql("SELECT * FROM vw_total_vendido_mes", engine)

df4 = pd.read_sql("SELECT * FROM vw_total_pedidos_meio_pagamento", engine)

df5 = pd.read_sql("SELECT * FROM vw_ticket_medio_clientes", engine)

df6 = pd.read_sql("SELECT * FROM vw_top_categorias", engine)

df7 = pd.read_sql("SELECT * FROM vw_tempo_medio_entre_pedidos", engine)

df8 = pd.read_sql("SELECT * from vw_qtd_faixa_etaria", engine)

df9 = pd.read_sql("select * from vw_venda_tipo_envio", engine)

st.set_page_config(layout="wide")

col1, col2 = st.columns(2)

fig_faturamento = px.bar(df3, x="ano_mes", y="total_vendido",color_discrete_sequence=["green"], title="Faturamento mensal")
fig_faturamento

fig_meio_pagamento = px.bar(df, x="pagamento_nome", y="total_vendido",title="Total vendido por Meio de Pagamento")
col1.plotly_chart(fig_meio_pagamento)

df2 = df2.sort_values("total_cliente", ascending=True)
fig_bairros = px.bar(df2, x="total_cliente", y="bairro",title="Top bairros", orientation="h",color="total_cliente",color_continuous_scale="Greens")
col2.plotly_chart(fig_bairros)

col3, col4 = st.columns(2)

fig_faixa_etaria = px.bar(df8, x="faixa_etaria", y="qtd_clientes",title="Total Cliente por faixa etaria")
col3.plotly_chart(fig_faixa_etaria)

df9 = df9.sort_values("total_envio", ascending=True)
fig_envios = px.bar(df9, x="total_envio", y="envio_nome",title="Vendas por tipo de envio", orientation="h")
col4.plotly_chart(fig_envios)
