import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard E-commerce",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header principal
st.markdown(
    '<h1 class="main-header" style="text-align: center;">🛒 Dashboard de Vendas E-commerce</h1>',
    unsafe_allow_html=True
)

hoje = datetime.today()

df_pedidos = pd.read_csv('data/processed/fato_vendas.csv')

df_pedidos['data_criacao'] = pd.to_datetime(df_pedidos['data_criacao'], errors='coerce', utc=True)

df_pedidos = df_pedidos[~df_pedidos['pedido_situacao'].isin(['Pedido Cancelado','Pagamento devolvido'])]

for col in ['valor_total', 'valor_envio']:
    if col in df_pedidos.columns:
        df_pedidos[col] = (
            df_pedidos[col]
            .astype(str)
            .str.strip()
            .str.replace(',', '.', regex=False)
            .replace('nan', None)
            .astype(float)
        )

# remove duplicados primeiro
df_filtrado = df_pedidos.drop_duplicates(subset=['pedido_numero']).copy()

# cria valor_venda
df_filtrado['valor_venda'] = df_filtrado['valor_total'] - df_filtrado['valor_envio']

# filtra últimos 12 meses
data_corte = pd.Timestamp.now(tz='UTC') - pd.DateOffset(months=12)
df_filtrado = df_filtrado[df_filtrado['data_criacao'] >= data_corte].copy()

# cria a coluna depois do filtro final
df_filtrado['data_formatada'] = df_filtrado['data_criacao'].dt.strftime('%Y/%m')

#funcao formatar moeda
def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# KPIs principais
col1, col2, col3, col4 = st.columns(4)

# função de filtro por mês/ano
def filtro_mes_ano(df, coluna_data, mes, ano):
    return df[
        (df[coluna_data].dt.month == mes) &
        (df[coluna_data].dt.year == ano)
    ]

# função de cálculo de delta (%)
def calcular_delta(valor_atual, valor_anterior):
    if valor_anterior != 0:
        return (valor_atual - valor_anterior) / valor_anterior * 100
    return 0


# mês atual
mes_atual = hoje.month
ano_atual = hoje.year

# mês anterior (tratando virada de ano)
mes_anterior = hoje.month - 1 if hoje.month > 1 else 12
ano_mes_anterior = hoje.year if hoje.month > 1 else hoje.year - 1

#card 1
faturamento_mensal_atual = filtro_mes_ano(
    df_filtrado, 'data_criacao', mes_atual, ano_atual
)['valor_venda'].sum()

faturamento_anterior = filtro_mes_ano(
    df_filtrado, 'data_criacao', mes_anterior, ano_mes_anterior
)['valor_venda'].sum()

delta = calcular_delta(
    faturamento_mensal_atual,
    faturamento_anterior
)

#card 2
qtdpedidos_mensal_atual = filtro_mes_ano(
    df_filtrado, 'data_criacao', mes_atual, ano_atual
)['pedido_numero'].nunique()

qtdpedidos_mes_anterior = filtro_mes_ano(
    df_filtrado, 'data_criacao', mes_anterior, ano_mes_anterior
)['pedido_numero'].nunique()

delta2 = calcular_delta(
    qtdpedidos_mensal_atual,
    qtdpedidos_mes_anterior
)

#card 3
ticket_medio_atual = faturamento_mensal_atual / qtdpedidos_mensal_atual
ticket_medio_anterior = faturamento_anterior / qtdpedidos_mes_anterior

delta3 = calcular_delta(
    ticket_medio_atual,
    ticket_medio_anterior
)

#card 4
total_produtos_mes_atual = filtro_mes_ano(
    df_pedidos, 'data_criacao', mes_atual, ano_atual
)['quantidade'].sum()

total_produtos_mes_anterior = filtro_mes_ano(
    df_pedidos, 'data_criacao', mes_anterior, ano_mes_anterior
)['quantidade'].sum()

delta4 = calcular_delta(
    total_produtos_mes_atual,
    total_produtos_mes_anterior
)
delta4 = (total_produtos_mes_atual - total_produtos_mes_anterior) / total_produtos_mes_anterior * 100

with col1:
    st.metric(
        label="💰 Faturamento Mês Atual",
        value=format_currency(faturamento_mensal_atual),
        delta=f"{delta:.2f}%"
    )

with col2:
    st.metric(
        label='🛍️ Qtd Pedido Mês Atual',
        value=qtdpedidos_mensal_atual,
        delta=f"{delta2:.2f}%"
    )

with col3:
    st.metric(
        label="🎯 Ticket Médio Mês Atual",
        value=format_currency(ticket_medio_atual),
        delta=f"{delta3:.2f}%"
    )

with col4:
    st.metric(
        label='🏷️ Total Produtos Vendidos',
        value=total_produtos_mes_atual,
        delta=f"{delta4:.2f}%"
    )

#primeiro grafico
df_last12 = (df_filtrado.groupby(['data_formatada'], as_index=False)['valor_venda']).sum()

fig_faturamento_last12 = px.bar(
    df_last12,
    x='data_formatada',
    y='valor_venda',
    text='valor_venda',
    title='Faturamento últimos 12 meses',
    labels={
        'data_formatada': 'Período',
        'valor_venda': 'Faturamento'
    }
)

fig_faturamento_last12.update_yaxes(range=[0, 40000])

fig_faturamento_last12.update_traces(
    texttemplate='R$ %{text:,.2f}',  # formato monetário
    textposition='outside',
    textfont=dict(size=14)
)

fig_faturamento_last12.update_layout(
    title_x=0.5
)

st.plotly_chart(fig_faturamento_last12, use_container_width=True)

#segunda linha de graficos
col1, col2, col3 = st.columns(3)

