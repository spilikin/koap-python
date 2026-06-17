import base64
import http.client as http_client
import logging

import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from rich.console import Console

from koap.client import ConnectorClient
from koap.config import AuthMethod, ConnectorConfig
from koap.debug import RichSoapDebugPlugin
from koap.facade.model import CertRefEnum, CryptEnum


def log_details(response, *args, **kwargs):
    print("Request URL:", response.request.url)
    for header, value in response.request.headers.items():
        print(f"Request Header: {header}: {value}")
    if response.request.body:
        print(
            "Request Body:",
            response.request.body.decode()
            if isinstance(response.request.body, bytes)
            else response.request.body,
        )
    print("Response Status Code:", response.status_code)
    for header, value in response.headers.items():
        print(f"Response Header: {header}: {value}")
    print("Response Body:", response.text)


debug_console = Console(record=True)
debug_plugin = RichSoapDebugPlugin(debug_console)

config = ConnectorConfig(
    # base_url="https://tig.spilikin.dev",
    #    mandant_id="Mandant2",
    #    workplace_id="AP200",
    #    client_system_id="CS200",
    #    auth_method=AuthMethod.cert,
    #    user_id="-",
    #    auth_cert_p12_filename="CS200.p12",
    #    auth_cert_p12_password="nse<$;gNJl|+LPcu",
    # danger_verify_tls=False,
)


client = ConnectorClient(config, soap_plugins=[debug_plugin])

client.transport.session.hooks["response"].append(log_details)

event_service = client.create_service_client("EventService", "7.2.0")

cards = event_service.GetCards(client.context())
print(cards)

cert_service = client.create_service_client("CertificateService", "6.0.1")

cert_responses = []
for card in cards.Cards.Card:
    print(card.CardHandle)
    try:
        cert_response = cert_service.ReadCardCertificate(
            CardHandle=card.CardHandle,
            Context=client.context(),
            CertRefList=[CertRefEnum.C_AUT.value],
            Crypt=CryptEnum.ECC.value,
        )
        print(cert_response)
        cert_responses.append(cert_response)
    except Exception as e:
        print(f"Failed to read certificate for card {card.CardHandle}: {e}")

for cert_response in cert_responses:
    cert_der = cert_response.X509DataInfoList.X509DataInfo[0].X509Data.X509Certificate
    cert = x509.load_der_x509_certificate(cert_der, default_backend())
    print(cert.subject)
    try:
        admission_ext = cert.extensions.get_extension_for_oid(
            x509.ObjectIdentifier("1.3.36.8.3.3")
        )
        print(f"Found extension: {admission_ext}")
        print(f"Extension value: {admission_ext.value}")
    except x509.ExtensionNotFound:
        print("Extension with OID 1.3.36.8.3.3 not found")
