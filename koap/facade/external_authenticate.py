from koap.client import ConnectorClient
from koap.facade.model import CardTypeEnum, obj_to_card

# cards which can be used for (external) authentication
AUTH_CARDS = [CardTypeEnum.HBA, CardTypeEnum.SMC_B, CardTypeEnum.HSM_B, CardTypeEnum.SM_B]


class ExternalAuthenticateFacade:
    def __init__(self, client: ConnectorClient):
        self.client = client
        self.event_service = client.create_service_client('EventService', '7.2.0')

    def get_auth_cards(self):
        get_cards_response = self.event_service.GetCards(
            Context=self.client.context()
        )
        raw_cards = filter(lambda c: c.CardType in AUTH_CARDS, get_cards_response.Cards.Card)
        return list(map(obj_to_card, raw_cards))
