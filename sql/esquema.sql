-- Modelo relacional da GS. Horários são gravados em UTC.
-- Não há cadastro de pessoas, documentos, telefones ou crianças.
CREATE TABLE IF NOT EXISTS municipios (
    id INT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    uf CHAR(2) NOT NULL,
    INDEX idx_uf_nome (uf, nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS anuncios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    tipo ENUM('doacao','pedido','permuta','oportunidade') NOT NULL,
    categoria ENUM('itens','aprendizagem','trabalho') NOT NULL,
    descricao VARCHAR(800) NOT NULL,
    contrapartida VARCHAR(200) NOT NULL DEFAULT '',
    municipio_id INT NOT NULL,
    status ENUM('aberto','reservado','concluido') NOT NULL DEFAULT 'aberto',
    versao INT NOT NULL DEFAULT 1,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (municipio_id) REFERENCES municipios(id),
    INDEX idx_conexao (municipio_id, categoria, tipo, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Fila transacional: anúncio e aviso são gravados no mesmo COMMIT.
-- Se o receptor TCP estiver indisponível, o aviso continua nesta tabela.
CREATE TABLE IF NOT EXISTS notificacoes (
    id CHAR(36) PRIMARY KEY,
    anuncio_id INT NOT NULL,
    acao ENUM('criar','atualizar','excluir') NOT NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    entregue_em DATETIME NULL,
    tentativas INT NOT NULL DEFAULT 0,
    INDEX idx_pendentes (entregue_em, criado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
