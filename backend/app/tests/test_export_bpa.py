from app.services.export_bpa import gerar_arquivo, LINE_LEN, HEADER_LEN, TRAILER_LEN, calc_checksum_bpa


def test_bpa_line_lengths_and_positions():
    procedimentos = [
        {
            "cnes": "1234560",
            "competencia": "202501",
            "cns_prof": "898001160660006",
            "cbo": "2231",
            "data_atendimento": "20250101",
            "procedimento": "1234567890",
            "cns_paciente": "898001160660006",
            "cpf_paciente": "",
            "sexo": "M",
            "cid": "F329",
            "idade": 30,
            "quantidade": 1,
            "valor": 10.0,
        }
    ]
    conteudo = gerar_arquivo(
        competencia="202501",
        orgao="CER",
        sigla="CER",
        cnpj="12345678000199",
        destino="M",
        versao="0.1",
        procedimentos=procedimentos,
    )
    linhas = conteudo.splitlines(keepends=True)
    header, linha_proc, trailer = linhas[0], linhas[1], linhas[2]
    assert header.endswith("\r\n")
    assert linha_proc.endswith("\r\n")
    assert trailer.endswith("\r\n")
    header_body = header.rstrip("\r\n")
    assert len(header_body) == HEADER_LEN
    assert len(linha_proc.rstrip("\r\n")) == LINE_LEN
    assert len(trailer.rstrip("\r\n")) == TRAILER_LEN
    # Literal 01 + #BPA# nas posicoes 1-7 (1-based)
    assert header_body[0:2] == "01"
    assert header_body[2:7] == "#BPA#"
    # Posições críticas (1-based): cnes começa na posição 1, procedimento na 43
    assert linha_proc[0:7] == "1234560"
    assert linha_proc[42:52] == "1234567890"
    # CNS pac no campo dedicado
    assert linha_proc[52:67] == "898001160660006"
    # Folha e sequência preenchidos (map inclui prd_flh e prd_seq)
    assert linha_proc[102:105] == "001"
    assert linha_proc[105:108] == "001"


def test_bpa_quantidade_folhas_calculo():
    procedimentos = []
    for _ in range(25):
        procedimentos.append({
            "cnes": "1234560",
            "competencia": "202501",
            "cns_prof": "898001160660006",
            "cbo": "2231",
            "data_atendimento": "20250101",
            "procedimento": "1234567890",
            "cns_paciente": "898001160660006",
            "cpf_paciente": "",
            "sexo": "M",
            "cid": "F329",
            "idade": 30,
            "quantidade": 1,
            "valor": 10.0,
        })
    conteudo = gerar_arquivo("202501", "CER", "CER", "12345678000199", "M", "0.1", procedimentos)
    header_body = conteudo.splitlines()[0]
    # quantidade_folhas posição 20-25 (1-based) -> indices 19:25
    assert header_body[19:25] == "000002"


def test_checksum_domain():
    procedures = [{"procedimento": "1234567890", "quantidade": 1}]
    cs = calc_checksum_bpa(procedures)
    assert 1111 <= cs <= 2221
