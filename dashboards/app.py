from datetime import datetime,date

import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title='Dashboard E-commerce',
    page_icon='🛒',
    layout='wide',
    initial_sidebar_state='expanded',
)

# Header principal
st.markdown(
    '<h1 class="main-header" style="text-align: center;">🛒 Dashboard de Vendas E-commerce</h1>',
    unsafe_allow_html=True,
)

hoje = datetime.today()

df_pedidos = pd.read_csv('data/processed/fato_vendas.csv')
df_clientes = pd.read_csv('data/processed/dim_cliente.csv')

df_pedidos['data_criacao'] = pd.to_datetime(
    df_pedidos['data_criacao'], errors='coerce', utc=True
)

df_pedidos = df_pedidos[
    ~df_pedidos['pedido_situacao'].isin(
        ['Pedido Cancelado', 'Pagamento devolvido']
    )
]

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
df_filtrado['valor_venda'] = (
    df_filtrado['valor_total'] - df_filtrado['valor_envio']
)

# filtra últimos 12 meses
data_corte = pd.Timestamp.now(tz='UTC') - pd.DateOffset(months=12)
df_filtrado = df_filtrado[df_filtrado['data_criacao'] >= data_corte].copy()

# cria a coluna depois do filtro final
df_filtrado['data_formatada'] = df_filtrado['data_criacao'].dt.strftime(
    '%Y/%m'
)

# funcao formatar moeda
def format_currency(value):
    return (
        f'R$ {value:,.2f}'.replace(',', 'X')
        .replace('.', ',')
        .replace('X', '.')
    )


# KPIs principais
col1, col2, col3, col4 = st.columns(4)

# função de filtro por mês/ano
def filtro_mes_ano(df, coluna_data, mes, ano):
    return df[
        (df[coluna_data].dt.month == mes) & (df[coluna_data].dt.year == ano)
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

# card 1
faturamento_mensal_atual = filtro_mes_ano(
    df_filtrado, 'data_criacao', mes_atual, ano_atual
)['valor_venda'].sum()

faturamento_anterior = filtro_mes_ano(
    df_filtrado, 'data_criacao', mes_anterior, ano_mes_anterior
)['valor_venda'].sum()

delta = calcular_delta(faturamento_mensal_atual, faturamento_anterior)

# card 2
qtdpedidos_mensal_atual = filtro_mes_ano(
    df_filtrado, 'data_criacao', mes_atual, ano_atual
)['pedido_numero'].nunique()

qtdpedidos_mes_anterior = filtro_mes_ano(
    df_filtrado, 'data_criacao', mes_anterior, ano_mes_anterior
)['pedido_numero'].nunique()

delta2 = calcular_delta(qtdpedidos_mensal_atual, qtdpedidos_mes_anterior)

# card 3
ticket_medio_atual = faturamento_mensal_atual / qtdpedidos_mensal_atual
ticket_medio_anterior = faturamento_anterior / qtdpedidos_mes_anterior

delta3 = calcular_delta(ticket_medio_atual, ticket_medio_anterior)

# card 4
total_produtos_mes_atual = filtro_mes_ano(
    df_pedidos, 'data_criacao', mes_atual, ano_atual
)['quantidade'].sum()

total_produtos_mes_anterior = filtro_mes_ano(
    df_pedidos, 'data_criacao', mes_anterior, ano_mes_anterior
)['quantidade'].sum()

delta4 = calcular_delta(total_produtos_mes_atual, total_produtos_mes_anterior)
delta4 = (
    (total_produtos_mes_atual - total_produtos_mes_anterior)
    / total_produtos_mes_anterior
    * 100
)

with col1:
    st.metric(
        label='💰 Faturamento Mês Atual',
        value=format_currency(faturamento_mensal_atual),
        delta=f'{delta:.2f}%',
    )

with col2:
    st.metric(
        label='🛍️ Qtd Pedido Mês Atual',
        value=qtdpedidos_mensal_atual,
        delta=f'{delta2:.2f}%',
    )

with col3:
    st.metric(
        label='🎯 Ticket Médio Mês Atual',
        value=format_currency(ticket_medio_atual),
        delta=f'{delta3:.2f}%',
    )

with col4:
    st.metric(
        label='🏷️ Total Produtos Vendidos',
        value=total_produtos_mes_atual,
        delta=f'{delta4:.2f}%',
    )

# primeiro grafico
df_last12 = df_filtrado.groupby(['data_formatada'], as_index=False)[
    'valor_venda'
].sum()

fig_faturamento_last12 = px.bar(
    df_last12,
    x='data_formatada',
    y='valor_venda',
    text='valor_venda',
    color_discrete_sequence=['#0E6AC5'],
    title='Faturamento últimos 12 meses',
    labels={'data_formatada': 'Período', 'valor_venda': 'Faturamento'},
)

fig_faturamento_last12.update_yaxes(range=[0, 40000])

fig_faturamento_last12.update_traces(
    texttemplate='R$ %{text:,.2f}',  # formato monetário
    textposition='outside',
    textfont=dict(size=14),
)

fig_faturamento_last12.update_layout(title_x=0.5)

st.plotly_chart(fig_faturamento_last12, use_container_width=True)

st.markdown('---')

# segunda linha de graficos
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('💳 Vendas por Pagamento Mês Atual')
    df_filtrado['pagamento_nome'] = df_filtrado['pagamento_nome'].replace(
        'MercadoPago V1', 'Mercado Pago'
    )

    pagamento_atual = filtro_mes_ano(
        df_filtrado, 'data_criacao', mes_atual, ano_atual
    )
    pagamento = pagamento_atual.groupby(['pagamento_nome'], as_index=False)[
        'valor_venda'
    ].sum()

    fig_payment = px.pie(
        pagamento,
        values='valor_venda',
        names='pagamento_nome',
        title='',
        hole=0.4,
    )
    fig_payment.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>',
    )
    fig_payment.update_layout(
        showlegend=True, legend=dict(orientation='h', yanchor='bottom', y=-0.2)
    )
    st.plotly_chart(fig_payment, use_container_width=True)

with col2:
    st.subheader('🏆 Top 5 Produtos Mês Atual')
    top5 = filtro_mes_ano(df_filtrado, 'data_criacao', mes_atual, ano_atual)
    contagem_produ = top5['produto_nome'].value_counts()
    top5 = contagem_produ.head(5)
    fig_top5 = px.bar(
        top5,
        x=top5.values,
        y=top5.index,
        orientation='h',
        color=top5.values,  # define intensidade da cor
        color_continuous_scale='purples',  # escala de cor (degradê)
        labels={'produto_nome': 'Produto', 'x': 'Total de Produtos'},
    )

    fig_top5.update_layout(
        yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False
    )

    fig_top5.update_traces(
        hovertemplate='<b>%{y}</b><br>Vendidos: %{x}<extra></extra>'
    )

    st.plotly_chart(fig_top5, use_container_width=True)


with col3:
    st.subheader('🚚 Tipo de Envio Mês Atual')
    envio_atual = filtro_mes_ano(
        df_filtrado, 'data_criacao', mes_atual, ano_atual
    )
    envio = envio_atual['envio_nome'].value_counts()

    fig_envio = px.pie(envio, values=envio.values, names=envio.index, hole=0.4)
    fig_envio.update_layout(
        showlegend=True, legend=dict(orientation='h', yanchor='bottom', y=-0.2)
    )

    st.plotly_chart(fig_envio, use_container_width=True)

st.markdown('---')

# Tabela de Top Clientes
st.subheader('👑 Melhores Clientes da Loja - Top10')

df_filtrado['ult_compr_form'] = df_filtrado['data_criacao'].dt.strftime('%d/%m/%Y')

top10_clientes = (
    df_filtrado.groupby('cpf_cliente')
    .agg(
        {
            'endereco_entrega_nome': 'first',
            'endereco_entrega_telefone_celular': 'first',
            'valor_venda': ['sum', 'count', 'mean'],
            'ult_compr_form':'first'
        }
    )
    .reset_index()
)


top10_clientes.columns = [
    'cpf_cliente',
    'nome',
    'telefone',
    'Total em Compras',
    'Quantidade de Compras',
    'Ticket Medio',
    'Última Compra'
]

top10_clientes = top10_clientes.sort_values(
    by='Total em Compras', ascending=False
)

top10_clientes['Ticket Medio'] = top10_clientes['Ticket Medio'].apply(
    format_currency
)
top10_clientes['Total em Compras'] = top10_clientes['Total em Compras'].apply(
    format_currency
)

top10_clientes = top10_clientes.drop(columns=['cpf_cliente', 'telefone'])

st.dataframe(
    top10_clientes.head(10), use_container_width=True, hide_index=True
)

st.markdown('---')

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Meta de Vendas Mensal")
    meta_vendas = 10000
    vendas_atual = faturamento_mensal_atual
    percentual_meta = (vendas_atual / meta_vendas) * 100

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=percentual_meta,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "% da Meta Atingida"},
        delta={'reference': 100, 'relative': False},
        gauge={
            'axis': {'range': [None, 100], 'ticksuffix': '%'},
            'bar': {'color': "#28a388"},
            'steps': [
                {'range': [0, 50], 'color': '#fee2e2'},
                {'range': [50, 75], 'color': '#fef3c7'},
                {'range': [75, 100], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    fig_gauge.update_layout(height=350)
    st.plotly_chart(fig_gauge, use_container_width=True)

from datetime import date
import pandas as pd

def calcular_idade(nascimento):
    if pd.isna(nascimento):
        return None
    
    hoje = date.today()
    
    idade = hoje.year - nascimento.year
    
    if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
        idade -= 1
        
    return idade

def classificar_faixa_etaria(idade):
    if pd.isna(idade):
        return 'Desconhecido'
    elif 0 <= idade <= 17:
        return '0 a 17 anos'
    elif 18 <= idade <= 23:
        return '18 a 23 anos'
    elif 24 <= idade <= 29:
        return '24 a 29 anos'
    elif 30 <= idade <= 35:
        return '30 a 35 anos'
    else:
        return 'Desconhecido'

df_clientes['data_nascimento'] = pd.to_datetime(df_clientes['data_nascimento'], errors='coerce')

df_clientes['idade'] = df_clientes['data_nascimento'].apply(calcular_idade)

df_clientes['faixa_etaria'] = df_clientes['idade'].apply(classificar_faixa_etaria)

age = (
    df_clientes.groupby('faixa_etaria', as_index=False)
    .size()
    .rename(columns={'size': 'qtd_clientes'})
    .sort_values('qtd_clientes', ascending=False)
)

age['percentual_clientes'] = round(
    age['qtd_clientes'] * 100 / age['qtd_clientes'].sum(), 2
).astype(str) + '%'

with col2:
    st.subheader("👥 Idade da Base de Clientes")
    fig_age = px.pie(
        age,
        values='qtd_clientes',
        names='faixa_etaria',
        title='',
        hole=0.4,
    )
    fig_age.update_layout(
        showlegend=True, legend=dict(orientation='h', yanchor='bottom', y=-0.2)
    )
    st.plotly_chart(fig_age, use_container_width=True)



