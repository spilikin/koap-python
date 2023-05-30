from koap.facade.epa.epa_facade import EPAFacade
from koap.client import ConnectorClient, ConnectorConfig
from koap.debug import RichSoapDebugPlugin
from rich.console import Console
import os


def test_epa_adhoc_authz():
    debug_console = Console(record=True)
    print = debug_console.print
    debug_plugin = RichSoapDebugPlugin(debug_console)

    try:
        client = ConnectorClient(ConnectorConfig(), soap_plugins=[debug_plugin])
        epa = EPAFacade(client)

        authorizations = epa.get_authorization_list()

        print(authorizations)

    finally:
        base_file_name = os.path.basename(__file__)  # get base file name, might include .py
        debug_plugin.save_html(os.path.splitext(base_file_name)[0]+'.html')
