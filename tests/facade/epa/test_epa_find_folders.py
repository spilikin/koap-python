from koap.facade.epa.epa_facade import EPAFacade, RecordId, InsurantId
from koap.facade.epa.epa_record_facade import EPARecordFacade
from koap.client import ConnectorClient, ConnectorConfig
from koap.debug import RichSoapDebugPlugin
from rich.console import Console
import os
from rich.table import Table


def test_epa_find_folders():
    debug_console = Console(record=True)
    print = debug_console.print
    debug_plugin = RichSoapDebugPlugin(debug_console)

    try:
        client = ConnectorClient(ConnectorConfig(), soap_plugins=[debug_plugin])
        epa = EPAFacade(client)
  
        # TODO: determine kvnr from local database or from card
        kvnr = 'X110476138'
        home_community_id = 'urn:oid:1.2.276.0.76.3.1.315.3.3.1.1'

        record_id = RecordId(HomeCommunityId=home_community_id, InsurantId=InsurantId(kvnr))

        epa_record = EPARecordFacade(epa, record_id)

        folders = epa_record.find_folders()

        table = Table(title="Folders")
        table.add_column("Name")

        for folder in folders:
            table.add_row(
                folder['Name']['LocalizedString']['@value'],
            )

        print(table)

    finally:
        base_file_name = os.path.basename(__file__)  # get base file name, might include .py
        debug_plugin.save_html(os.path.splitext(base_file_name)[0]+'.html')
