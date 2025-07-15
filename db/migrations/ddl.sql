-- =======================================
-- TABELAS DO PROJETO SALES ECOMMERCE
-- =======================================

-- =====================
-- TABELA: dim_cliente
-- =====================
CREATE TABLE dim_cliente (
    cpf               CHAR(11)    PRIMARY KEY,
    email             TEXT,
    nome              TEXT        NOT NULL,
    data_nascimento   DATE,
    telefone_celular  TEXT,
    endereco          TEXT,
    bairro            TEXT,
    cidade            TEXT,
    estado            CHAR(2),
    cep               CHAR(8),
    data_criacao      DATE
);

-- =====================
-- TABELA: dim_produto
-- =====================
CREATE TABLE dim_produto (
    id_produto        BIGINT      PRIMARY KEY,
    sku_pai           TEXT,
    sku               TEXT        UNIQUE NOT NULL,
    nome              TEXT        NOT NULL,
    categoria         TEXT
);

-- =====================
-- TABELA: fato_vendas
-- =====================
CREATE TABLE fato_vendas (
    id                             SERIAL PRIMARY KEY,
    pedido_numero                  INT         NOT NULL,
    cpf_cliente                    CHAR(11)     NOT NULL REFERENCES dim_cliente(cpf),
    cliente_email                  TEXT,
    pedido_situacao                TEXT,
    pagamento_nome                 TEXT,
    envio_nome                     TEXT,
    valor_subtotal                 NUMERIC,
    valor_envio                    NUMERIC,
    valor_desconto                 NUMERIC,
    valor_total                    NUMERIC,
    peso_real                      NUMERIC,
    data_criacao                   DATE,
    -- Informações de entrega
    endereco_entrega_nome          TEXT,
    endereco_entrega_telefone_celular TEXT,
    endereco_entrega_logradouro    TEXT,
    endereco_entrega_numero        TEXT,
    endereco_entrega_bairro        TEXT,
    endereco_entrega_cidade        TEXT,
    endereco_entrega_cep           CHAR(8),
    -- Dados do item
    produto_id                     BIGINT       NOT NULL REFERENCES dim_produto(id_produto),
    produto_sku                    TEXT,
    produto_nome                   TEXT,
    quantidade                     INT,
    preco_venda                    NUMERIC,
    preco_promocional              NUMERIC,
    preco_custo                    NUMERIC,
    -- Restrição: Evita duplicidade do mesmo produto no mesmo pedido
    UNIQUE(pedido_numero, produto_id)
);
