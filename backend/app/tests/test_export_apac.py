from app.services.export_apac import gerar_arquivo, HEADER_LEN, CORPO_LEN, PROC_LEN, calc_checksum_apac


def test_apac_lengths_and_positions():
    corpo = {
        "competencia": "202501",
        "numero_apac": "1234567890123",
        "uf": "11",
        "cnes": "1234560",
        "data_processamento": "20250101",
        "data_inicio_validade": "20250101",
        "data_fim_validade": "20250301",
        "tipo_atendimento": "01",
        "tipo_apac": "1",
        "nome_paciente": "Paciente Teste",
        "nome_mae": "Mae Teste",
        "logradouro": "Rua Teste",
        "numero_endereco": "123",
        "complemento": "Ap 10",
        "cep": "70000000",
        "municipio_ibge": "1100015",
        "data_nascimento": "19900101",
        "sexo": "M",
        "nome_medico_responsavel": "Resp Teste",
        "procedimento_principal": "1234567890",
        "motivo_saida": "01",
        "data_obito_alta": "",
        "nome_autorizador": "Diretor",
        "cns_paciente": "898001160660006",
        "cns_medico_resp": "898001160660006",
        "cns_autorizador": "898001160660006",
        "cid_associado": "F329",
        "num_prontuario": "0000000001",
        "cnes_solicitante": "1234567",
        "data_solicitacao": "20250101",
        "data_autorizacao": "20250101",
        "codigo_emissor": "1234567890",
        "carater_atendimento": "01",
        "apac_anterior": "",
        "raca_cor": "99",
        "nome_responsavel": "Mae Teste",
        "nacionalidade": "010",
        "etnia": "",
        "cod_logradouro_ibge": "001",
        "bairro": "Centro",
        "ddd": "61",
        "fone": "999999999",
        "email": "a@b.com",
        "cns_executor": "898001160660006",
        "cpf_paciente": "",
        "ine": "1234567890",
        "pessoa_rua": "N",
        "fonte_orc": "00",
        "emenda": "N",
        "fim": "  ",
    }
    procedimentos = [
        {"numero_apac": "1234567890123", "codigo": "1234567890", "quantidade": 1},
    ]
    conteudo = gerar_arquivo("202501", "CER", "CER", "12345678000199", "SES", "0.1", corpo, procedimentos)
    linhas = conteudo.splitlines(keepends=True)
    header, corpo_line, proc_line = linhas[0], linhas[1], linhas[2]
    assert header.endswith("\r\n")
    assert corpo_line.endswith("\r\n")
    assert proc_line.endswith("\r\n")
    header_body = header.rstrip("\r\n")
    corpo_body = corpo_line.rstrip("\r\n")
    proc_body = proc_line.rstrip("\r\n")
    assert len(header_body) == HEADER_LEN
    assert len(corpo_body) == CORPO_LEN
    assert len(proc_body) == PROC_LEN
    # Header literal #APAC nas posicoes 3-7 (1-based)
    assert header_body[2:7] == "#APAC"
    # Indicador emissao/recepcao (1-based 114)
    assert header_body[113] in {"M", "E"}
    # CNS paciente na posicao 267-281 (1-based)
    assert corpo_body[266:281] == "898001160660006"
    # Nome mae posicao 88-117
    assert corpo_body[87:117] == "Mae Teste".ljust(30)
    # CEP posicao 163-170
    assert corpo_body[162:170] == "70000000"
    # CNS medico resp posicao 282-296
    assert corpo_body[281:296] == "898001160660006"
    # Carater posicao 359-360
    assert corpo_body[358:360] == "01"
    # Email posicao 457-496
    assert corpo_body[456:496].strip().startswith("a@b.com")
    # Campo fim (filler) presente antes do CRLF
    assert corpo_body[536:538] == "  "
    # CBO default preenchido no proc (1-based 32-37)
    assert proc_body[31:37] == "000000"


def test_apac_checksum_domain():
    procedures = [{"numero_apac": "1", "codigo": "1234567890", "quantidade": 2}]
    cs = calc_checksum_apac(procedures, "1")
    assert 1111 <= cs <= 2221


def test_apac_checksum_not_duplicated_per_proc():
    numero = "1234567890123"
    procs_one = [{"numero_apac": numero, "codigo": "1234567890", "quantidade": 1}]
    procs_two = [
        {"numero_apac": numero, "codigo": "1234567890", "quantidade": 1},
        {"numero_apac": numero, "codigo": "1234567890", "quantidade": 1},
    ]
    cs_one = calc_checksum_apac(procs_one, numero)
    cs_two = calc_checksum_apac(procs_two, numero)
    codigo_digits = "1234567890"
    codigo_base = codigo_digits[:-1]
    delta_esperado = int(codigo_base) + 1  # codigo base + quantidade adicional
    assert cs_two - cs_one == delta_esperado % 1111
