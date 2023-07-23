from koap.facade.epa.epa_facade import EPAFacade, RecordId, InsurantId
from koap.facade.epa.epa_record_facade import EPARecordFacade, classification_slot_by_name
from koap.client import ConnectorClient, ConnectorConfig
from koap.debug import RichSoapDebugPlugin
from rich.console import Console
from rich.table import Table

import os


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

        documents = epa_record.find_documents()

        table = Table(title="Documents")
        table.add_column("Name")
        table.add_column("Author")
        for document in documents:
            table.add_row(
                document['Name']['LocalizedString']['@value'],
                classification_slot_by_name(document, 'authorPerson')['ValueList']['Value'],
                
            )

        print(table)

    finally:
        base_file_name = os.path.basename(__file__)  # get base file name, might include .py
        debug_plugin.save_html(os.path.splitext(base_file_name)[0]+'.html')
