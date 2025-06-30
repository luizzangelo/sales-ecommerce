import pandas as pd

# Lê os CSVs da pasta staging
df_pedidos = pd.read_csv('data/staging/pedidos.csv')
df_clientes = pd.read_csv('data/staging/clientes.csv')
df_produtos = pd.read_csv('data/staging/produtos.csv')

# Apenas para testar se tudo está funcionando
#print("✅ Dados carregados para transformação:")
#print("Pedidos:", df_pedidos.shape)
#print("Clientes:", df_clientes.shape)
#print("Produtos:", df_produtos.shape)

import numpy as np

# 1. Substitui strings vazias por NaN
df_produtos["nome"] = df_produtos["nome"].replace("", np.nan)
df_produtos["categoria-nome-nivel-1"] = df_produtos["categoria-nome-nivel-1"].replace("", np.nan)

# 2. Identifica linhas “pai” (onde sku-pai está vazio ou NaN)
mask_pai = df_produtos["sku-pai"].isna() | (df_produtos["sku-pai"] == "")

# 3. Gera mapeamento sku → nome do produto
parent_names = df_produtos.loc[mask_pai, ["sku", "nome"]].set_index("sku")["nome"].to_dict()

# 4. Gera mapeamento sku → categoria
parent_cats = df_produtos.loc[mask_pai, ["sku", "categoria-nome-nivel-1"]].set_index("sku")["categoria-nome-nivel-1"].to_dict()

# 5. Preenche nome e categoria das variações
df_produtos["nome"] = df_produtos["nome"].fillna(df_produtos["sku-pai"].map(parent_names))
df_produtos["categoria-nome-nivel-1"] = df_produtos["categoria-nome-nivel-1"].fillna(df_produtos["sku-pai"].map(parent_cats))

# 6. Preenche faltantes com texto padrão
df_produtos["nome"] = df_produtos["nome"].fillna("NOME NÃO ENCONTRADO")
df_produtos["categoria-nome-nivel-1"] = df_produtos["categoria-nome-nivel-1"].fillna("CATEGORIA NÃO ENCONTRADA")

# 7. Seleciona colunas finais para a dimensão produto
df_dim_produto = df_produtos[["id", "sku-pai", "sku", "nome", "categoria-nome-nivel-1"]].copy()

print("\n✅ Dimensão produto tratada:")
#print(df_dim_produto.head(10))

# TRATAR OS PEDIDOS
from tabulate import tabulate
import ast
import json

linhas = []

for idx, row in df_pedidos.iterrows():
    try:
        lista_de_strings = ast.literal_eval(row['ITEMS_JSON'])

        for item_str in lista_de_strings:
            item = json.loads(item_str)

            linhas.append({
                'CLIENTE_EMAIL'         : row['CLIENTE_EMAIL'],
                'PEDIDO_NUMERO'         : row['PEDIDO_NUMERO'],
                'PEDIDO_DATA_CRIACAO'   : pd.to_datetime(row['PEDIDO_DATA_CRIACAO'], dayfirst=True, utc=True),
                'produto_id'            : item.get('produto_id'),
                'produto_nome'          : item.get('produto_nome'),
                'produto_sku'           : item.get('produto_sku'),
                'quantidade'            : item.get('quantidade', 1),
                'preco_venda'           : item.get('preco_venda', 0),
                'preco_promocional'     : item.get('preco_promocional', 0),
                'preco_custo'           : item.get('preco_custo', 0),
            })

    except Exception as e:
        print(f"Erro na linha {idx}: {e}")

# Converte em DataFrame de fato
df_fato_vendas = pd.DataFrame(linhas)

print("\n✅ Fato vendas criado:")
#print(tabulate(df_fato_vendas.head(5), headers='keys', tablefmt='psql'))

# TRATAR A DIMENSÃO CLIENTE
# Normaliza nome de colunas para trabalhar apenas com as relevantes
colunas_cliente = [
    "id",
    "email",
    "nome",
    "data-nascimento",
    "cpf",
    "telefone-celular",
    "endereco",
    "bairro",
    "cidade",
    "estado",
    "cep",
    "data-criacao"
]

# Garante que só vamos trabalhar com essas colunas
df_dim_cliente = df_clientes[colunas_cliente].copy()

# Converte colunas de data
df_dim_cliente["data-nascimento"] = pd.to_datetime(df_dim_cliente["data-nascimento"], errors="coerce", dayfirst=True)
df_dim_cliente["data-criacao"] = pd.to_datetime(df_dim_cliente["data-criacao"], errors="coerce", dayfirst=True)

print("\n✅ Dimensão cliente criada:")
#print(df_dim_cliente.head(3))

import os

# Cria pasta processed se não existir
os.makedirs('data/processed', exist_ok=True)

# Salva os DataFrames tratados
df_dim_produto.to_csv('data/processed/dim_produto.csv', index=False)
df_dim_cliente.to_csv('data/processed/dim_cliente.csv', index=False)
df_fato_vendas.to_csv('data/processed/fato_vendas.csv', index=False)

print("\n✅ Arquivos salvos em data/processed/")

