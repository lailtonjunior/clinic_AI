"""
Utilidades de validacao de DV e formatos (CNS, CNES, SIGTAP, CPF, CID).
"""

import re


class ValidationException(Exception):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


def validate_cns(cns: str) -> bool:
    """
    Valida CNS (15 digitos) conforme regra DATASUS.
    - Cartao definitivo inicia com 1 ou 2: derivado do PIS/PASEP (11 digitos) + sufixo 001 + DV.
    - Cartao provisorio inicia com 7, 8 ou 9 e valida por modulo 11 do numero completo.
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
    Valida CNES (7 digitos) usando modulo 11 com pesos [7,6,5,4,3,2] no corpo.
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
    Valida codigo de procedimento SIGTAP.
    - Aceita 7 digitos numericos (formato simplificado).
    - Aceita 10 digitos com DV modulo 11 sobre os 9 primeiros digitos (pesos crescentes 1..9).
    """
    if not codigo or not codigo.isdigit():
        return False
    if len(codigo) == 7:
        return True
    if len(codigo) != 10:
        return False
    corpo, dv_str = codigo[:9], codigo[9]
    soma = sum(int(corpo[i]) * (i + 1) for i in range(9))
    dv = soma % 11
    if dv == 10:
        dv = 0
    return dv == int(dv_str)


def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF (11 digitos) com os dois digitos verificadores.
    Aceita caracteres de formatacao (., -) e ignora entradas com todos os digitos iguais.
    """
    if not cpf:
        return False
    numeros = re.sub(r"\D", "", cpf)
    if len(numeros) != 11 or len(set(numeros)) == 1:
        return False

    def _calcula_dv(sequencia: str, peso_inicial: int) -> int:
        soma = sum(int(dig) * peso for dig, peso in zip(sequencia, range(peso_inicial, 1, -1)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    dv1 = _calcula_dv(numeros[:9], 10)
    dv2 = _calcula_dv(numeros[:10], 11)
    return numeros[-2:] == f"{dv1}{dv2}"


_CID_PATTERN = re.compile(r"^[A-TV-Z]\d{2}(?:\.[0-9A-TV-Z]{1,4})?$")


def validate_cid(cid: str) -> bool:
    """
    Valida formato de CID-10/CID-11 basico: letra, dois digitos e opcional sufixo (. + 1-4 alfanumericos).
    """
    if not cid:
        return False
    return bool(_CID_PATTERN.match(cid.upper()))

