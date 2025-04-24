select * from receitas r 
select * from medicamentos m 
select * from usuarios u 
select * from saidas s
select * from entradas e 

--- Renomear a coluna para que a senha não fique explícita no código
ALTER TABLE usuarios RENAME COLUMN senha TO senha_hash

--- Adicionar o registro de usuário a tabela medicamentos
ALTER TABLE medicamentos
ADD COLUMN usuario_id INTEGER NOT NULL;

ALTER TABLE medicamentos
ADD CONSTRAINT fk_medicamento_usuario
FOREIGN KEY (usuario_id)
REFERENCES usuarios(id);

