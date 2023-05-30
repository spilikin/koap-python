from koap.facade.epa.epa_facade import EPAFacade, RecordId
from koap.client import ConnectorClient, ConnectorConfig
from koap.debug import RichSoapDebugPlugin
from rich.console import Console
import os
import datetime


def test_epa_adhoc_authz():
    debug_console = Console(record=True)
    print = debug_console.print
    debug_plugin = RichSoapDebugPlugin(debug_console)

    try:
        client = ConnectorClient(ConnectorConfig(), soap_plugins=[debug_plugin])
        epa = EPAFacade(client)
        egks, smcbs = epa.get_cards()

        print("[bold blue]Got me some eGKs[/bold blue]]")
        print(egks)

        print("[bold blue]Got me some SMC-Bs[/bold blue]]")
        print(smcbs)

        # TODO: determine kvnr
        kvnr = 'X110476138'

        home_community_id = epa.get_home_community_id(kvnr)

        epa.request_facility_authorization(
            egks[0],
            smcbs[0],
            RecordId(home_community_id, kvnr),
            [
                "practitioner",
                "hospital",
                "laboratory",
                "physiotherapy",
                "psychotherapy",
                "dermatology",
                "gynaecology_urology",
                "dentistry_oms",
                "other_medical",
                "other_non_medical",
                "emp",
                "nfd",
                "eab",
                "dentalrecord",
                "childsrecord",
                "mothersrecord",
                "vaccination",
                "patientdoc",
                "ega",
                "receipt",
                "care",
                "prescription",
                "eau",
                "other",
            ],
            expiration_date=datetime.date(2024, 12, 31)
        )

    finally:
        base_file_name = os.path.basename(__file__)  # get base file name, might include .py
        debug_plugin.save_html(os.path.splitext(base_file_name)[0]+'.html')
