from koap.client import ConnectorClient
from pydantic import BaseModel
from koap.facade.model import CardTypeEnum
from koap.facade.model import obj_to_card, Card, CARD_TYPES_SMCB
from typing import Tuple, List
import datetime


class InsurantId(BaseModel):
    extension: str
    root: str = "1.2.276.0.76.4.8"

    def __init__(self, kvnr: str):
        super().__init__(extension=kvnr)


class RecordId(BaseModel):
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
