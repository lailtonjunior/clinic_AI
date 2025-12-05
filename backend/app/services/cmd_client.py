import httpx
from typing import Tuple, Dict, Any, List
from xml.etree import ElementTree as ET


NS_SOAP = "http://schemas.xmlsoap.org/soap/envelope/"
NS_WSSE = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
NS_CMD = "http://servicos.saude.gov.br/ws/cmd/v1r0/contatoassistencialservice"


def _ns(tag: str, ns: str) -> str:
    return f"{{{ns}}}{tag}"


def build_ws_security_header(username: str, password: str) -> ET.Element:
    security = ET.Element(_ns("Security", NS_WSSE))
    token = ET.SubElement(security, _ns("UsernameToken", NS_WSSE))
    user_el = ET.SubElement(token, _ns("Username", NS_WSSE))
    user_el.text = username
    pwd_el = ET.SubElement(token, _ns("Password", NS_WSSE))
    pwd_el.text = password
    return security


def build_autenticacao_cmd_header(cpf: str, senha: str) -> ET.Element:
    auth = ET.Element("autenticacaoCMD")
    cpf_el = ET.SubElement(auth, "cpf")
    cpf_el.text = cpf
    senha_el = ET.SubElement(auth, "senha")
    senha_el.text = senha
    return auth


def build_envelope(body: ET.Element, headers: List[ET.Element]) -> str:
    envelope = ET.Element(_ns("Envelope", NS_SOAP))
    header = ET.SubElement(envelope, _ns("Header", NS_SOAP))
    for h in headers:
        header.append(h)
    body_el = ET.SubElement(envelope, _ns("Body", NS_SOAP))
    body_el.append(body)
    return ET.tostring(envelope, encoding="unicode")


class CmdSoapClient:
    def __init__(self, wsdl_url: str, usuario_servico: str, senha_servico: str, cpf_operador: str, senha_operador: str):
        self.wsdl_url = wsdl_url
        self.usuario_servico = usuario_servico
        self.senha_servico = senha_servico
        self.cpf_operador = cpf_operador
        self.senha_operador = senha_operador

    def _headers(self) -> Dict[str, str]:
        return {"Content-Type": "text/xml; charset=utf-8"}

    def _post(self, xml_envelope: str) -> httpx.Response:
        with httpx.Client(timeout=30.0) as client:
            return client.post(self.wsdl_url, content=xml_envelope.encode("utf-8"), headers=self._headers())

    def _parse_response(self, response: httpx.Response) -> Tuple[int, str, Any]:
        try:
            tree = ET.fromstring(response.text)
            fault = tree.find(f".//{{{NS_SOAP}}}Fault")
            if fault is not None:
                faultstring = fault.find("faultstring")
                return response.status_code, "FAULT", faultstring.text if faultstring is not None else "Erro SOAP"
            # Busca codigoRetorno/mensagem
            codigo = tree.find(".//codigoRetorno")
            mensagem = tree.find(".//mensagemRetorno")
            return response.status_code, (codigo.text if codigo is not None else ""), (mensagem.text if mensagem is not None else "")
        except ET.ParseError:
            return response.status_code, "PARSE_ERROR", response.text

    def _base_headers(self) -> List[ET.Element]:
        return [
            build_ws_security_header(self.usuario_servico, self.senha_servico),
            build_autenticacao_cmd_header(self.cpf_operador, self.senha_operador),
        ]

    def incluir_contato(self, dados_xml: ET.Element) -> Tuple[int, str, Any]:
        body = ET.Element("incluirContatoAssistencial")
        body.append(dados_xml)
        envelope = build_envelope(body, self._base_headers())
        resp = self._post(envelope)
        return self._parse_response(resp)

    def alterar_contato(self, dados_xml: ET.Element) -> Tuple[int, str, Any]:
        body = ET.Element("alterarContatoAssistencial")
        body.append(dados_xml)
        envelope = build_envelope(body, self._base_headers())
        resp = self._post(envelope)
        return self._parse_response(resp)

    def cancelar_contato(self, uuid_cmd: str, motivo: str) -> Tuple[int, str, Any]:
        body = ET.Element("cancelarContatoAssistencial")
        req = ET.SubElement(body, "RequestCancelarContatoAssistencial")
        ET.SubElement(req, "uuidContatoAssistencial").text = uuid_cmd
        ET.SubElement(req, "motivoCancelamento").text = motivo
        envelope = build_envelope(body, self._base_headers())
        resp = self._post(envelope)
        return self._parse_response(resp)

    def pesquisar_contato(self, competencia: str, cnes: str, cns: str) -> Tuple[int, str, Any]:
        body = ET.Element("pesquisarContatoAssistencial")
        req = ET.SubElement(body, "RequestPesquisarContatoAssistencial")
        ET.SubElement(req, "competencia").text = competencia
        ET.SubElement(req, "cnes").text = cnes
        ET.SubElement(req, "cns").text = cns
        envelope = build_envelope(body, self._base_headers())
        resp = self._post(envelope)
        return self._parse_response(resp)

    def detalhar_contato(self, uuid_cmd: str) -> Tuple[int, str, Any]:
        body = ET.Element("detalharContatoAssistencial")
        req = ET.SubElement(body, "RequestDetalharContatoAssistencial")
        ET.SubElement(req, "uuidContatoAssistencial").text = uuid_cmd
        envelope = build_envelope(body, self._base_headers())
        resp = self._post(envelope)
        return self._parse_response(resp)
