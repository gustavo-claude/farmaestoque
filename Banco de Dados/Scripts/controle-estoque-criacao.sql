-- Tabela medicamentos
CREATE TABLE medicamentos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    principio_ativo VARCHAR(255),
    laboratorio VARCHAR(255),
    codigo_barras VARCHAR(255) UNIQUE,
    preco_custo DECIMAL(10, 2),
    preco_venda DECIMAL(10, 2),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR (11) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    nivel_acesso VARCHAR(50) NOT NULL
);

-- alter table usuarios add cpf varchar(11) unique not null;
ALTER TABLE usuarios RENAME COLUMN senha TO senha_hash

-- Tabela receitas
CREATE TABLE receitas (
    id SERIAL PRIMARY KEY,
    codigo_receita VARCHAR(255) UNIQUE NOT NULL,
    data_emissao DATE NOT NULL,
    paciente_nome VARCHAR(255),
    medico_nome VARCHAR(255),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id)
);

-- Tabela entradas
CREATE TABLE entradas (
    id SERIAL PRIMARY KEY,
    medicamento_id INTEGER NOT NULL REFERENCES medicamentos(id),
    quantidade INTEGER NOT NULL,
    data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lote VARCHAR(255),
    data_validade DATE,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id)
);

-- Tabela saidas
CREATE TABLE saidas (
    id SERIAL PRIMARY KEY,
    medicamento_id INTEGER NOT NULL REFERENCES medicamentos(id),
    quantidade INTEGER NOT NULL,
    data_saida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_saida VARCHAR(50) NOT NULL,
    receita_id INTEGER REFERENCES receitas(id),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id)
);

