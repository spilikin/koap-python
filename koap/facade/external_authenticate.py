from koap.client import ConnectorClient
from koap.facade.model import (
    CardTypeEnum,
    Card,
    obj_to_card,
    CryptEnum,
    CertRefEnum,
)
from typing import List

# cards which can be used for (external) authentication
AUTH_CARDS = [CardTypeEnum.HBA, CardTypeEnum.SMC_B, CardTypeEnum.HSM_B, CardTypeEnum.SM_B]


class ExternalAuthenticateFacade:
    def __init__(self, client: ConnectorClient):
        self.client = client
        self.event_service = client.create_service_client('EventService', '7.2.0')
        self.card_service = client.create_service_client('CardService', '8.1.2')
        self.certificate_service = client.create_service_client('CertificateService', '6.0.1')
        self.auth_signature_service = client.create_service_client('AuthSignatureService', '7.4.1')

    def get_auth_cards(self) -> List[Card]:
        get_cards_response = self.event_service.GetCards(
            Context=self.client.context()
        )
        raw_cards = filter(lambda c: c.CardType in AUTH_CARDS, get_cards_response.Cards.Card)
        return list(map(obj_to_card, raw_cards))

    def get_card_certificates(self, card_handle: str, cert_types: List[CertRefEnum], crypt: CryptEnum):
        response = self.certificate_service.ReadCardCertificate(
            CardHandle=card_handle,
            Context=self.client.context(),
            CertRefList=list(map(lambda cert_type: cert_type.value, cert_types)),
            Crypt=crypt.value,
        )

        return response.X509DataInfoList.X509DataInfo

    def verify_pin(self, card_type: CardTypeEnum, card_handle: str) -> any:
        if card_type == CardTypeEnum.SMC_B:
            pin_type = "PIN.SMC"
        else:
            pin_type = "PIN.CH"
        return self.card_service.VerifyPin(
            self.client.context(),
            card_handle,
            pin_type
        )

    def external_authenticate(self, card_handle: str, hash: bytes, crypt: CertRefEnum) -> bytes:
        if crypt == "RSA":
            optional_outputs = {
                'SignatureType': 'urn:ietf:rfc:3447',
                'SignatureSchemes': 'RSASSA-PSS'
            }
        else:
            optional_outputs = {
                'SignatureType': 'urn:bsi:tr:03111:ecdsa',
            }

        response = self.auth_signature_service.ExternalAuthenticate(
            CardHandle=card_handle,
            Context=self.client.context(),
            OptionalInputs=optional_outputs,
            BinaryString={
                "Base64Data": {
                    "MimeType": "application/octet-stream",
                    "_value_1": hash
                }
            }
        )

        return response.SignatureObject.Base64Signature._value_1
