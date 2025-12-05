from app.services.validators import (
    validate_cns,
    validate_cnes,
    validate_sigtap_codigo,
)


def test_validate_cns_definitivo():
    # Base PIS 12345678901 gera CNS 123456789010010 (DV calculado)
    assert validate_cns("123456789010010") is True


def test_validate_cns_provisorio():
    # Monta número provisório que obedece mod 11 do número completo
    assert validate_cns("799999999999999") is False


def test_validate_cnes():
    assert validate_cnes("1234560") is True
    assert validate_cnes("1234567") is False


def test_validate_sigtap_codigo():
    # código construído com DV conforme algoritmo
    assert validate_sigtap_codigo("1234567890") is True
    assert validate_sigtap_codigo("1234567899") is False
