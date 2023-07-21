from koap.facade.external_authenticate import (
    ExternalAuthenticateFacade,
    CardTypeEnum,
    CertRefEnum,
    CryptEnum,
)
from koap.client import ConnectorClient, ConnectorConfig
from koap.debug import RichSoapDebugPlugin
from rich.console import Console
import os

debug_console = Console(record=True)
print = debug_console.print


def test_external_authenticate():
    try:
        debug_plugin = RichSoapDebugPlugin(debug_console)
        client = ConnectorClient(ConnectorConfig(), soap_plugins=[debug_plugin])
        ext_auth = ExternalAuthenticateFacade(client)
        # get all auth cards
        auth_cards = ext_auth.get_auth_cards()
        # get first SMC-B card
        smcb_1 = next(filter(lambda card: card.CardType == CardTypeEnum.SMC_B, auth_cards))

        # random hash of 256 bits (32 bytes) to sign
        hash_to_sign = os.urandom(32)

        # get RSA AUT certificate
        _ = ext_auth.get_card_certificates(smcb_1.CardHandle, [CertRefEnum.C_AUT], CryptEnum.RSA)

        rsa_signature = ext_auth.external_authenticate(smcb_1.CardHandle, hash_to_sign, CryptEnum.RSA)
        print("RSA Signature:")
        print(rsa_signature)

        try:
            # get ECC AUT certificate
            ecc_aut_cert = ext_auth.get_card_certificates(smcb_1.CardHandle, [CertRefEnum.C_AUT], CryptEnum.ECC)
            print(ecc_aut_cert)

            ecc_signature = ext_auth.external_authenticate(smcb_1.CardHandle, hash_to_sign, CryptEnum.ECC)
            print("ECC Signature:")
            print(ecc_signature)
        except Exception as e:
            print(f"Warning: {e}")
    finally:
        base_file_name = os.path.basename(__file__)  # get base file name, might include .py
        debug_plugin.save_html(os.path.splitext(base_file_name)[0]+'.html')

