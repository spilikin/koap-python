from koap.facade.vsdm.vsdm_facade import VSDMFacade
from koap.facade.model import CardTypeEnum
from koap.client import ConnectorClient, ConnectorConfig
from koap.debug import RichSoapDebugPlugin
from rich.console import Console
import os

debug_console = Console(record=True)
print = debug_console.print


def test_read_vsd():
    try:
        debug_plugin = RichSoapDebugPlugin(debug_console)
        client = ConnectorClient(ConnectorConfig(), soap_plugins=[debug_plugin])

        print(client.service_directory)

        vsdm = VSDMFacade(client)

        egks = vsdm.get_cards([CardTypeEnum.EGK])
        egk_1 = egks[0]

        print(egk_1)

        smcbs = vsdm.get_cards([CardTypeEnum.SMC_B])
        smcb_1 = smcbs[0]

        print(smcb_1)

        vsd = vsdm.read_vsd(
            EhcHandle=egk_1.CardHandle,
            HpcHandle=smcb_1.CardHandle,
            PerformOnlineCheck=False,
            ReadOnlineReceipt=False,
        )

        print(vsd)

    finally:
        base_file_name = os.path.basename(__file__)  # get base file name, might include .py
        debug_plugin.save_html(os.path.splitext(base_file_name)[0]+'.html')

