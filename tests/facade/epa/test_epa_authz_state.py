from koap.facade.epa.epa_facade import EPAFacade, RecordId
from koap.client import ConnectorClient, ConnectorConfig
from koap.debug import RichSoapDebugPlugin
from rich.console import Console
import os


def test_epa_authz_state():
    debug_console = Console(record=True)
    print = debug_console.print
    debug_plugin = RichSoapDebugPlugin(debug_console)

    try:
        client = ConnectorClient(ConnectorConfig(), soap_plugins=[debug_plugin])

        print("[bold blue]Services[/bold blue]]")
        print(client.service_directory)

        epa = EPAFacade(client)
        egks, _ = epa.get_cards()

        print("[bold blue]Got me some eGKs[/bold blue]]")
        print(egks)

        # TODO: determine kvnr
        kvnr = 'X110476138'

        home_community_id = epa.get_home_community_id(kvnr)

        authz_state = epa.get_authorization_state(RecordId(home_community_id, kvnr))

        print(authz_state)
    finally:
        base_file_name = os.path.basename(__file__)  # get base file name, might include .py
        debug_plugin.save_html(os.path.splitext(base_file_name)[0]+'.html')
