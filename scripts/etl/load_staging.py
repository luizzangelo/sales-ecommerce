import pandas as pd
df_pedidos = pd.read_excel('/Users/luizangelo/Documents/sales-ecommerce/data/import_manual/LISTAR_PEDIDOS.xlsx')
df_clientes = pd.read_excel('/Users/luizangelo/Documents/sales-ecommerce/data/import_manual/EXPORTAR_CLIENTES.xlsx')
df_produtos = pd.read_excel('/Users/luizangelo/Documents/sales-ecommerce/data/import_manual/LISTA DE PRODUTOS.xlsx')

import os

# 1. Certifica que a pasta staging existe
os.makedirs('data/staging', exist_ok=True)

# 2. Salva cada DataFrame como CSV em staging
df_pedidos.to_csv('data/staging/pedidos.csv', index=False)
df_clientes.to_csv('data/staging/clientes.csv', index=False)
df_produtos.to_csv('data/staging/produtos.csv', index=False)

print("✅ Staging pronto: pedidos.csv, clientes.csv e produtos.csv gerados em data/staging/")
