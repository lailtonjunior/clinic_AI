HEADER_BPA_2025 = [
    {"name": "indicador", "start": 1, "length": 2, "default": "01"},
    {"name": "marcador", "start": 3, "length": 5, "default": "#BPA#"},
    {"name": "competencia", "start": 8, "length": 6, "required": True},
    {"name": "quantidade_linhas", "start": 14, "length": 6, "required": True, "pad": "0"},
    {"name": "quantidade_folhas", "start": 20, "length": 6, "required": True, "pad": "0"},
    {"name": "checksum", "start": 26, "length": 4, "required": True, "pad": "0"},
    {"name": "orgao_nome", "start": 30, "length": 30, "required": True},
    {"name": "orgao_sigla", "start": 60, "length": 6, "required": True},
    {"name": "cnpj", "start": 66, "length": 14, "required": True},
    {"name": "orgao_destino", "start": 80, "length": 40, "required": True},
    {"name": "destino", "start": 120, "length": 1, "required": True},
    {"name": "versao", "start": 121, "length": 10, "required": True},
    {"name": "fim", "start": 131, "length": 2, "required": False, "default": "  "},
]

LINHA_BPA_2025 = [
    {"name": "cnes", "start": 1, "length": 7, "required": True},
    {"name": "competencia", "start": 8, "length": 6, "required": True},
    {"name": "cns_prof", "start": 14, "length": 15, "required": True},
    {"name": "cbo", "start": 29, "length": 6, "required": True},
    {"name": "data_atendimento", "start": 35, "length": 8, "required": True},
    {"name": "procedimento", "start": 43, "length": 10, "required": True},
    {"name": "cns_paciente", "start": 53, "length": 15, "required": False},
    {"name": "cpf_paciente", "start": 68, "length": 11, "required": False},
    {"name": "sexo", "start": 79, "length": 1, "required": True},
    {"name": "cid", "start": 80, "length": 4, "required": True},
    {"name": "idade", "start": 84, "length": 3, "required": True, "pad": "0"},
    {"name": "quantidade", "start": 87, "length": 6, "required": True, "pad": "0"},
    {"name": "valor", "start": 93, "length": 10, "required": False, "pad": "0"},
    {"name": "prd_flh", "start": 103, "length": 3, "required": False, "pad": "0"},
    {"name": "prd_seq", "start": 106, "length": 3, "required": False, "pad": "0"},
]

TRAILER_BPA_2025 = [
    {"name": "identificador", "start": 1, "length": 6, "default": "99#BPA#"},
    {"name": "total_procedimentos", "start": 7, "length": 6, "required": True, "pad": "0"},
    {"name": "valor_total", "start": 13, "length": 12, "required": True, "pad": "0"},
    {"name": "checksum", "start": 25, "length": 4, "required": True, "pad": "0"},
]
