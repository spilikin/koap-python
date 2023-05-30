from koap.facade.epa.epa_facade import EPAFacade, RecordId, EPARecordFacade
from koap.client import ConnectorClient, ConnectorConfig
from koap.debug import RichSoapDebugPlugin
from rich.console import Console
import os


def test_epa_get_folders():
    debug_console = Console(record=True)
    print = debug_console.print
    debug_plugin = RichSoapDebugPlugin(debug_console)

    try:
        client = ConnectorClient(ConnectorConfig(), soap_plugins=[debug_plugin])
        epa = EPAFacade(client)

        # TODO: determine kvnr
        kvnr = 'X110476138'
        home_community_id = 'urn:oid:1.2.276.0.76.3.1.315.3.3.1.1'

        record_id = RecordId(home_community_id, kvnr)

        epa_record = EPARecordFacade(epa, record_id)

        response = epa_record.get_folders()

        print(response)

    finally:
        base_file_name = os.path.basename(__file__)  # get base file name, might include .py
        debug_plugin.save_html(os.path.splitext(base_file_name)[0]+'.html')
