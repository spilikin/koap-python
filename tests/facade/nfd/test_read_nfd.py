from koap.config import ConnectorConfig
from koap.client import ConnectorClient
from koap.facade.model import CardTypeEnum
from koap.facade.external_authenticate import ExternalAuthenticateFacade
from koap.debug import RichSoapDebugPlugin
from rich.console import Console
import os

debug_console = Console(record=True)
print = debug_console.print


def test_read_nfd():
    try:
        debug_plugin = RichSoapDebugPlugin(debug_console)
        client = ConnectorClient(ConnectorConfig(), soap_plugins=[debug_plugin])
        ext_auth = ExternalAuthenticateFacade(client)

        event_service = client.create_service_client('EventService', '7.2.0')

        cards = event_service.GetCards(client.context())

        first_egk = next(filter(lambda c: c.CardType == CardTypeEnum.EGK, cards.Cards.Card))
        print(first_egk.CardHandle)

        first_hba = next(filter(lambda c: c.CardType == CardTypeEnum.HBA, cards.Cards.Card))
        print(first_hba.CardHandle)

        nfd_service = client.create_service_client('NFDService', '1.0.0', "nfds")

        ext_auth = ExternalAuthenticateFacade(client)

        ext_auth.verify_pin(first_hba.CardType, first_hba.CardHandle)

        nfd = nfd_service.ReadNFD(
            client.context(),
            first_egk.CardHandle,
            first_hba.CardHandle,
            True,
            False,
        )

        print(nfd)

    finally:
        base_file_name = os.path.basename(__file__)  # get base file name, might include .py
        debug_plugin.save_html(os.path.splitext(base_file_name)[0]+'.html')

