from koap.client import ConnectorClient
from pydantic import BaseModel
from koap.facade.model import CardTypeEnum
from koap.facade.model import obj_to_card, Card, CARD_TYPES_SMCB
from typing import Tuple, List
import datetime
from zeep import xsd


class InsurantId(BaseModel):
    extension: str
    root: str = "1.2.276.0.76.4.8"


class RecordId(BaseModel):
    def __init__(self, home_community_id: str, kvnr: str):
        super().__init__(InsurantId=InsurantId(extension=kvnr), HomeCommunityId=home_community_id)

    HomeCommunityId: str
    InsurantId: InsurantId


class EPAFacade:
    def __init__(self, client: ConnectorClient):
        self.client = client
        self.phr_mgt_service = client.create_service_client('PHRManagementService', '2.0.1', module="phrs")
        self.phr_service = client.create_service_client('PHRService', '2.0.1', module="phrs", binding_local_name='PHRService_Binding_Soap12')
        self.event_service = client.create_service_client('EventService', '7.2.0')

    def get_home_community_id(self, kvnr: str):
        response = self.phr_mgt_service.GetHomeCommunityID(
            Context=self.client.context(),
            InsurantID=InsurantId(extension=kvnr).dict(),
        )
        # TODO: camelcase ID
        return response['HomeCommunityID']

    def get_authorization_list(self):
        response = self.phr_mgt_service.GetAuthorizationList(
            Context=self.client.context(),
        )
        return response['AuthorizationList']['_value_1']

    def get_cards(self) -> Tuple[List[Card], List[Card]]:
        get_cards_response = self.event_service.GetCards(
            Context=self.client.context()
        )
        raw_egks = filter(lambda c: c.CardType in [CardTypeEnum.EGK], get_cards_response.Cards.Card)
        raw_smcbs = filter(lambda c: c.CardType in CARD_TYPES_SMCB, get_cards_response.Cards.Card)
        return list(map(obj_to_card, raw_egks)), list(map(obj_to_card, raw_smcbs))

    def request_facility_authorization(
            self, 
            egk: Card, 
            smcb: Card, 
            record_id: RecordId,
            categories: List[str],
            expiration_date: datetime.date
            ):
        response = self.phr_mgt_service.RequestFacilityAuthorization(
            Context=self.client.context(),
            EhcHandle=egk.CardHandle,
            # TODO: woher weiss man das?
            AuthorizationConfiguration={
                'AuthorizationConfidentiality': 'normal',
                'DocumentCategoryList': {
                    '_value_1': list(map(lambda c: {'DocumentCategoryElement': c}, categories)),
                },
                # TODO: set date
                'ExpirationDate': expiration_date
            },
            RecordIdentifier=record_id.dict(),
            OrganizationName=smcb.CardHolderName,
            # TODO: Vorname und Nachname: Deutsch(!) wo kommt das her? 
            InsurantName={"Vorname": egk.CardHolderName, "Nachname": egk.CardHolderName},
        )
        return response

    def get_authorization_state(self, record_id: RecordId):
        response = self.phr_mgt_service.GetAuthorizationState(
            Context=self.client.context(),
            RecordIdentifier=record_id.dict(),
            # TODO: get koap name and version
            UserAgent="koap/0.1.0/spilikin",
        )
        return response


class EPARecordFacade:
    def __init__(self, epa_facade: EPAFacade, record_id: RecordId):
        self.epa_facade = epa_facade
        self.record_id = record_id

    def get_folders(self):
        response = self.epa_facade.phr_service.DocumentRegistry_RegistryStoredQuery(
            federated=False,
            startIndex=0,
            maxResults=-1,
            ResponseOption={
                'returnType': 'LeafClass',
                'returnComposedObjects': True
            },
            AdhocQuery={
                'id': 'urn:uuid:958f3006-baad-4929-a4de-ff1114824431',
                'home': self.record_id.HomeCommunityId,
                'Slot': [
                    {
                        'name': '$XDSFolderStatus',
                        "ValueList": {
                            "_value_1": [
                                {
                                    'Value': "('urn:oasis:names:tc:ebxml-regrep:StatusType:Approved')"
                                }
                            ]
                        }
                    },
                    {
                        'name': "$XDSFolderPatientId",
                        "ValueList": {
                            "_value_1": [
                                {
                                    'Value': f"('{self.record_id.InsurantId.extension}^^^&1.2.276.0.76.4.8&ISO')"
                                }
                            ]
                        }
                    }
                ]
            },
            _soapheaders=self.soap_headers()
        )

        from koap.util import element_to_obj

        def folder_to_obj(folder):
            return element_to_obj(folder, single_elements=['LocalizedString'])

        folders = map(folder_to_obj, response['RegistryObjectList']['_raw_elements'])
        return list(folders)
    
    def soap_headers(self) -> List:
        header = xsd.Element(
            '{http://ws.gematik.de/conn/phrs/PHRService/v2.0}ContextHeader',
            xsd.ComplexType([
                xsd.Element('{http://ws.gematik.de/conn/ConnectorContext/v2.0}Context', xsd.ComplexType([
                    xsd.Element('{http://ws.gematik.de/conn/ConnectorCommon/v5.0}MandantId', xsd.String()),
                    xsd.Element('{http://ws.gematik.de/conn/ConnectorCommon/v5.0}ClientSystemId', xsd.String()),
                    xsd.Element('{http://ws.gematik.de/conn/ConnectorCommon/v5.0}WorkplaceId', xsd.String()),
                    xsd.Element('{http://ws.gematik.de/conn/ConnectorCommon/v5.0}UserId', xsd.String()),
                ])),
                xsd.Element('{http://ws.gematik.de/conn/phrs/PHRService/v2.0}RecordIdentifier', xsd.ComplexType([
                    xsd.Element('{http://ws.gematik.de/fa/phr/v1.1}InsurantId', xsd.ComplexType(
                        attributes=[xsd.Attribute('root', xsd.String()), xsd.Attribute('extension', xsd.String())]
                    )),
                    xsd.Element('{http://ws.gematik.de/fa/phr/v1.1}HomeCommunityId', xsd.String()),
                ])
                )
            ])
        )

        return [header(Context=self.epa_facade.client.context(), RecordIdentifier=self.record_id.dict())]
