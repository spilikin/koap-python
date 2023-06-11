from koap.client import ConnectorClient
from koap.facade.model import (
    CardTypeEnum,
    Card,
    obj_to_card,
    CryptEnum,
    CertRefEnum,
)
from typing import List
from pydantic import BaseModel
import gzip
import xmltodict
from zeep.helpers import serialize_object


class VSD(BaseModel):
    PersoenlicheVersichertendaten: dict
    AllgemeineVersicherungsdaten: dict
    GeschuetzteVersichertendaten: dict
    Pruefungsnachweis: dict
    VSD_Status: dict


class VSDMFacade:
    def __init__(self, client: ConnectorClient):
        self.client = client
        self.event_service = client.create_service_client('EventService', '7.2.0')
        self.vsd_service = client.create_service_client('VSDService', '5.2.0', module="vsds")        

    def get_cards(self, types: List[CardTypeEnum] = None) -> List[Card]:
        get_cards_response = self.event_service.GetCards(
            Context=self.client.context()
        )
        raw_cards = get_cards_response.Cards.Card
        if types is not None:
            raw_cards = filter(lambda c: c.CardType in types, raw_cards)
        return list(map(obj_to_card, raw_cards))

    def get_card_certificates(self, card_handle: str, cert_types: List[CertRefEnum], crypt: CryptEnum):
        response = self.certificate_service.ReadCardCertificate(
            CardHandle=card_handle,
            Context=self.client.context(),
            CertRefList=list(map(lambda cert_type: cert_type.value, cert_types)),
            Crypt=crypt.value,
        )

        return response.X509DataInfoList.X509DataInfo

    def read_vsd(self, EhcHandle: str, HpcHandle: str, PerformOnlineCheck: bool, ReadOnlineReceipt: bool) -> VSD:
        response = self.vsd_service.ReadVSD(
            Context=self.client.context(),
            EhcHandle=EhcHandle,
            HpcHandle=HpcHandle,
            PerformOnlineCheck=PerformOnlineCheck,
            ReadOnlineReceipt=ReadOnlineReceipt,
        )

        return VSD(
            PersoenlicheVersichertendaten=self.vsd_data_to_dict(response, 'PersoenlicheVersichertendaten'),
            AllgemeineVersicherungsdaten=self.vsd_data_to_dict(response, 'AllgemeineVersicherungsdaten'),
            GeschuetzteVersichertendaten=self.vsd_data_to_dict(response, 'GeschuetzteVersichertendaten'),
            Pruefungsnachweis=self.vsd_data_to_dict(response, 'Pruefungsnachweis'),
            VSD_Status=serialize_object(response['VSD_Status']),
        )

    def vsd_data_to_dict(self, response: dict, field_name: str) -> dict:
        compressed_data = response[field_name]
        # gunzip comnpresed data
        data = gzip.decompress(compressed_data)
        xml_as_dict = xmltodict.parse(data)
        # first value in the dict
        xml_as_dict = xml_as_dict[list(xml_as_dict.keys())[0]]
        return xml_as_dict