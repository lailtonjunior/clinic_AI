"""
Utilidades de validação de DV (CNS, CNES, SIGTAP) seguindo regras DATASUS.
"""


def validate_cns(cns: str) -> bool:
    """
    Valida CNS (15 dígitos) conforme regra DATASUS.
    - Cartão definitivo inicia com 1 ou 2 e é derivado do PIS/PASEP (11 dígitos) + sufixo 001 + DV.
    - Cartão provisório inicia com 7, 8 ou 9 e valida por módulo 11 do número completo.
    """
    if not cns or len(cns) != 15 or not cns.isdigit():
        return False

    primeiro = cns[0]
    if primeiro in {"1", "2"}:
        base = cns[:11]
        soma = sum(int(base[i]) * (15 - i) for i in range(11))
        resto = soma % 11
        dv = 11 - resto
        if dv == 11:
            dv = 0
        elif dv == 10:
            soma += 2
            dv = 11 - (soma % 11)
        esperado = f"{base}001{dv}"
        return cns == esperado

    if primeiro in {"7", "8", "9"}:
        soma = sum(int(cns[i]) * (15 - i) for i in range(15))
        return soma % 11 == 0

    return False


def validate_cnes(cnes: str) -> bool:
    """
    Valida CNES (7 dígitos) usando módulo 11 com pesos [7,6,5,4,3,2] no corpo.
    """
    if not cnes or len(cnes) != 7 or not cnes.isdigit():
        return False
    corpo, dv_str = cnes[:6], cnes[6]
    pesos = [7, 6, 5, 4, 3, 2]
    soma = sum(int(corpo[i]) * pesos[i] for i in range(6))
    resto = soma % 11
    dv = 11 - resto
    if dv in (10, 11):
        dv = 0
    return dv == int(dv_str)


def validate_sigtap_codigo(codigo: str) -> bool:
    """
    Valida código de procedimento SIGTAP (10 dígitos) com DV módulo 11 sobre os 9 primeiros dígitos.
    Pesos crescentes 1..9. Se DV resultar em 10, usa DV=0.
    """
    if not codigo or len(codigo) != 10 or not codigo.isdigit():
        return False
    corpo, dv_str = codigo[:9], codigo[9]
    soma = sum(int(corpo[i]) * (i + 1) for i in range(9))
    dv = soma % 11
    if dv == 10:
        dv = 0
    return dv == int(dv_str)
