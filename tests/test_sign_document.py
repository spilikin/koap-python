from koap.client import ConnectorClient, ConnectorConfig, ConnectorServiceName
from koap.facade.model import CardTypeEnum
from koap.debug import RichSoapDebugPlugin
from rich.console import Console
import os
import base64
from lxml import etree

debug_console = Console(record=True)
print = debug_console.print


def test_read_vsd():
    try:
        debug_plugin = RichSoapDebugPlugin(debug_console)
        client = ConnectorClient(ConnectorConfig(), soap_plugins=[debug_plugin])
        
        # read NFD file from script directory
        nfd_path = os.path.join(os.path.dirname(__file__), "NFD_sample_1.4.xml")
        # nfd_path = os.path.join("/tmp/test.xml")
        nfd_bytes = open(nfd_path, "rb").read() 

        run_dir = os.getcwd()
        os.chdir(os.path.dirname("koap/api-telematik/fa/nfds/"))
        schema_root = etree.fromstring(open("NFD_Document_v1_4.xsd", "rb").read())

        schema = etree.XMLSchema(schema_root)

        os.chdir(run_dir)

        print(schema)

        nfd_root = etree.fromstring(nfd_bytes)

        schema.assertValid(nfd_root)

        sign_service = client.create_service_client(ConnectorServiceName.SignatureService, '7.5.5')

        event_service = client.create_service_client('EventService', '7.2.0')

        cards = event_service.GetCards(client.context())

        first_hba = next(filter(lambda c: c.CardType == CardTypeEnum.HBA, cards.Cards.Card))

        print(first_hba)

        print(nfd_bytes.decode("ISO-8859-15"))

        exit(nfd_root.attrib["ID"])

        """
          <ns10:SignRequest RequestID="QES821236567">
            <ns10:OptionalInputs>
              <ns5:SignatureType>urn:ietf:rfc:3275</ns5:SignatureType>
              <ns5:SignaturePlacement CreateEnvelopedSignature="false" WhichDocument="QES821236567">
                <ns5:XPathFirstChildOf>/*[local-name()='NFD_Document']/*[local-name()='SignatureArzt']</ns5:XPathFirstChildOf>
              </ns5:SignaturePlacement>
              <ns11:GenerateUnderSignaturePolicy>
                <ns11:SignaturePolicyIdentifier>urn:gematik:fa:sak:nfdm:r1:v1</ns11:SignaturePolicyIdentifier>
              </ns11:GenerateUnderSignaturePolicy>
            </ns10:OptionalInputs>
            <ns10:Document ID="QES821236567" RefURI="#ID1" ShortText="NFD_sample_1.4.xml">
              <ns8:Base64XML>Base64XML_GQ6cHJvdmlkZXI+DQoJCQk8ZWhkOnBlcnNvbj4NCgkJCQk8</ns8:Base64XML>
            </ns10:Document>
            <ns10:IncludeRevocationInfo>true</ns10:IncludeRevocationInfo>
          </ns10:SignRequest>        
        """

        sign_service.SignDocument(
            CardHandle=first_hba.CardHandle,
            Context=client.context(),
            TvMode="NONE",
            JobNumber="MVE-113",
            SignRequest={
                "RequestID": "REQID1234567890",
                "OptionalInputs": {
                    "SignatureType": "urn:ietf:rfc:3275",
                    "SignaturePlacement": {
                        "CreateEnvelopedSignature": False,
                        "WhichDocument": "DOCID1234567890",
                        "XPathFirstChildOf": "/*[local-name()='NFD_Document']/*[local-name()='SignatureArzt']"
                    },
                    "GenerateUnderSignaturePolicy": {
                        "SignaturePolicyIdentifier": "urn:gematik:fa:sak:nfdm:r1:v1"
                    }
                },
                "Document": {
                    "ID": "DOCID1234567890",
                    "RefURI": "#"+"",
                    "ShortText": "NFD_sample_1.4.xml",
                    "Base64XML": base64.b64encode(nfd_bytes).decode("utf-8")
                },
                "IncludeRevocationInfo": True
            }
        )

    finally:
        base_file_name = os.path.basename(__file__)  # get base file name, might include .py
        debug_plugin.save_html(os.path.splitext(base_file_name)[0]+'.html')

