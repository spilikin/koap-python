import asyncio
import socket
import logging
import ssl
import xmltodict
from requests_pkcs12 import create_sslcontext


logger = logging.getLogger(__name__)


class CETP:
    def __init__(self, on_event):
        self.on_event = on_event

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        magic = await reader.read(4)
        if magic != b'CETP':
            raise Exception('Invalid protocol')
        len_bytes = await reader.read(4)
        message_len = int.from_bytes(len_bytes, byteorder='big')
        event = await reader.read(message_len)
        logger.debug(f'Received event: {event}')
        writer.close()
        self.on_event(xmltodict.parse(event.decode()))

    def _ssl_context(self):
        ssl_ctx = create_sslcontext(
            pkcs12_data=open('/Users/serg/Downloads/c1.p12', 'rb').read(),
            pkcs12_password_bytes='1finger'.encode(),
            ssl_protocol=ssl.PROTOCOL_TLS_SERVER
        )
        # ssl_ctx.load_verify_locations(cafile='intermediate_ca.crt')
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = False
        return ssl_ctx
    
    async def start_server(self, host: str = None, port: int = 12201) -> asyncio.Server:
        if host is None:
            hostname = socket.gethostname()
            host = socket.gethostbyname(hostname)

        self._server = await asyncio.start_server(
            self._handle_client, host, port,
            ssl=self._ssl_context()
        )

        coroutine = self._server.serve_forever()
        logger.debug(f'Serving on {host}:{port}')

        return coroutine

    async def stop_server(self):
        self._server.close()
        await self._server.wait_closed()

