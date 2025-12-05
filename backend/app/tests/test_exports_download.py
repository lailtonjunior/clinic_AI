import asyncio
from fastapi.responses import StreamingResponse

from app.api.routes.core import _build_download_response


async def _collect(resp: StreamingResponse) -> bytes:
    chunks = []
    async for chunk in resp.body_iterator:
        chunks.append(chunk)
    return b"".join(chunks)


def test_download_response_headers_and_body():
    conteudo = "HEADER\r\nBODY\r\n"
    resp: StreamingResponse = _build_download_response(conteudo, "arquivo_test.rem")
    body = asyncio.run(_collect(resp))
    assert resp.headers["Content-Disposition"].endswith("arquivo_test.rem\"")
    assert resp.media_type.startswith("text/plain")
    assert body.endswith(b"\r\n")
    assert len(body) > 0
