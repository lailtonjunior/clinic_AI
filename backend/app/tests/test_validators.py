from app.services.validators import (
    validate_cns,
    validate_cnes,
    validate_sigtap_codigo,
    validate_cpf,
    validate_cid,
)


def test_validate_cns_definitivo():
    assert validate_cns("123456789010010") is True


def test_validate_cns_provisorio():
    assert validate_cns("799999999999999") is False


def test_validate_cnes():
    assert validate_cnes("1234560") is True
    assert validate_cnes("1234567") is False


def test_validate_sigtap_codigo():
    assert validate_sigtap_codigo("1234567890") is True
    assert validate_sigtap_codigo("1234567899") is False
    assert validate_sigtap_codigo("1234567") is True


def test_validate_cpf():
    assert validate_cpf("529.982.247-25") is True
    assert validate_cpf("12345678900") is False


def test_validate_cid():
    assert validate_cid("A00") is True
    assert validate_cid("B20.0") is True
    assert validate_cid("123") is False
    assert validate_cid("AA0") is False
