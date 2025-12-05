import httpx
from app.services import cmd_client
from xml.etree import ElementTree as ET


class DummyResponse(httpx.Response):
    def __init__(self, text: str, status_code: int = 200):
        super().__init__(status_code=status_code, content=text.encode("utf-8"))


def test_build_envelope_contains_headers():
    ws = cmd_client.build_ws_security_header("user", "pass")
    auth = cmd_client.build_autenticacao_cmd_header("12345678901", "senha")
    body = ET.Element("dummyBody")
    xml = cmd_client.build_envelope(body, [ws, auth])
    assert "UsernameToken" in xml
    assert "12345678901" in xml
    assert "dummyBody" in xml


def test_incluir_contato_sends_payload(monkeypatch):
    sent = {}

    class FakeClient(cmd_client.CmdSoapClient):
        def _post(self, xml_envelope: str):
            sent["xml"] = xml_envelope
            # retorno sucesso com codigoRetorno=0
            resp_xml = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
              <soapenv:Body>
                <incluirContatoAssistencialResponse>
                  <codigoRetorno>0</codigoRetorno>
                  <mensagemRetorno>Sucesso</mensagemRetorno>
                </incluirContatoAssistencialResponse>
              </soapenv:Body>
            </soapenv:Envelope>
            """
            return DummyResponse(resp_xml, status_code=200)

    client = FakeClient("http://test", "u", "p", "cpf", "s")
    body = ET.Element("RequestIncluirContatoAssistencial")
    status, codigo, msg = client.incluir_contato(body)
    assert status == 200
    assert codigo == "0"
    assert "Sucesso" in msg
    assert "RequestIncluirContatoAssistencial" in sent["xml"]
