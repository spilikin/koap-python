from typing import Any, List, Mapping
from .epa_facade import EPAFacade, RecordId
from lxml import etree
import xmltodict
from uuid import uuid4
from . import builder
from zeep.exceptions import TransportError, Fault


# very quick and dirty hack to remove the namespace prefix and convert to dict
def etree_to_dict(el: etree.ElementBase):
    for el2 in el.findall('.//*'):
        if el2.tag.startswith('{'):
            el2.tag = el2.tag.split('}', 1)[1]

    as_dist = xmltodict.parse(etree.tostring(el, encoding='utf8', method='xml', pretty_print=True))

    # get the value of the fist entry in dict
    as_dist = as_dist[list(as_dist.keys())[0]]

    return as_dist


class EPARecordFacade:
    def __init__(self, epa_facade: EPAFacade, record_id: RecordId):
        self.epa_facade = epa_facade
        self.record_id = record_id
        self.session = epa_facade.phr_service._client.transport.session
        self.address: str = epa_facade.phr_service._binding_options['address']
        self.plugins = epa_facade.phr_service._client.plugins
        if self.plugins is None:
            self.plugins = []

    def find_folders(self) -> List[Mapping[str, Any]]:
        soap_body = builder.Soap12Body(
            builder.AdhocQueryRequest(
                builder.ResponseOption(returnType="LeafClass", returnComposedObjects="true"),
                builder.AdhocQuery(
                    builder.Slot(
                        builder.ValueList(
                            builder.Value("('urn:oasis:names:tc:ebxml-regrep:StatusType:Approved')")
                        ),
                        name="$XDSFolderStatus"
                    ),
                    builder.Slot(
                        builder.ValueList(
                            builder.Value(f"('{self.record_id.InsurantId.extension}^^^&amp;1.2.276.0.76.4.8&amp;ISO')")
                        ),
                        name="$XDSFolderPatientId"
                    ),
                    id="urn:uuid:958f3006-baad-4929-a4de-ff1114824431",
                    home=self.record_id.HomeCommunityId,
                ),
                federated="false",
                startIndex="0",
                maxResults="-1",
            )
        )

        query_response = self.soap12_call('DocumentRegistry_RegistryStoredQuery', soap_body)

        return query_response['AdhocQueryResponse']['RegistryObjectList']['RegistryPackage']

    def get_folders_and_contents(self, folder_uuid) -> Mapping[str, Any]:
        soap_body = builder.Soap12Body(
            builder.AdhocQueryRequest(
                builder.ResponseOption(returnType="LeafClass", returnComposedObjects="true"),
                builder.AdhocQuery(
                    builder.Slot(
                        builder.ValueList(
                            builder.Value(f"'{folder_uuid}'")
                        ),
                        name="$XDSFolderEntryUUID"
                    ),
                    id="urn:uuid:b909a503-523d-4517-8acf-8e5834dfc4c7",
                    home=self.record_id.HomeCommunityId,
                ),
                federated="false",
                startIndex="0",
                maxResults="-1",
            )
        )

        query_response = self.soap12_call('DocumentRegistry_RegistryStoredQuery', soap_body)

        return query_response['AdhocQueryResponse']['RegistryObjectList']

    def find_documents(self) -> Any:
        soap_body = builder.Soap12Body(
            builder.AdhocQueryRequest(
                builder.ResponseOption(returnType="LeafClass", returnComposedObjects="true"),
                builder.AdhocQuery(
                    builder.Slot(
                        builder.ValueList(
                            builder.Value("('urn:oasis:names:tc:ebxml-regrep:StatusType:Approved')")
                        ),
                        name="$XDSDocumentEntryStatus"
                    ),
                    builder.Slot(
                        builder.ValueList(
                            builder.Value(f"('{self.record_id.InsurantId.extension}^^^&amp;1.2.276.0.76.4.8&amp;ISO')")
                        ),
                        name="$XDSDocumentEntryPatientId"
                    ),
                    id="urn:uuid:14d4debf-8f97-4251-9a74-a90016b0af0d",
                    home=self.record_id.HomeCommunityId,
                ),
                federated="false",
                startIndex="0",
                maxResults="-1",
            )
        )

        query_response = self.soap12_call('DocumentRegistry_RegistryStoredQuery', soap_body)

        return query_response['AdhocQueryResponse']['RegistryObjectList']['ExtrinsicObject']

    def soap_http_headers(self, soap_action: str) -> Mapping[str, str]:
        return {
            'Content-Type': f'application/soap+xml; charset=utf-8; action="{soap_action}"',
            # 'SOAPAction': soap_action,
        }

    def soap_header(self, soap_action: str) -> etree.Element:
        messageID = uuid4()
        return builder.Soap12Header(
            builder.ContextHeader(
                builder.Context(self.epa_facade.client.context()),
                builder.RecordIdentifier(
                    builder.InsurantId(root='1.2.276.0.76.4.8', extension=self.record_id.InsurantId.extension),
                    builder.HomeCommunityId(self.record_id.HomeCommunityId)
                ),
            ),
            builder.Action(soap_action),
            builder.MessageID(str(messageID)),
            builder.To(self.address),
            builder.ReplyTo(
                builder.Address('http://www.w3.org/2005/08/addressing/anonymous')
            ),
            builder.homeCommunityBlock(
                builder.homeCommunityId(self.record_id.HomeCommunityId)
            )
        )

    def soap12_call(self, operation_name: str, soap_body: etree.Element) -> etree.Element:
        # Zeep SOAP Operation we will be calling manuelly
        operation = self.epa_facade.phr_service._binding._operations[operation_name]
        # SOAP Action from Zeep Operation
        soap_action = operation.soapaction

        # prepare SOAP Envelpe XML Element
        message = builder.Soap12Envelope(
            self.soap_header(soap_action),
            soap_body
        )

        # Prepare HTTP Headers
        http_headers = self.soap_http_headers(soap_action)

        # Notify plugins, that request is incoming
        for plugin in self.plugins:
            plugin.egress(message, http_headers, operation, None)

        # serialize SOAP Envelope to XML string
        post_data = etree.tostring(message, pretty_print=True).decode()

        # perform HTTP POST to WebService
        response = self.session.post(
            self.address,
            headers=http_headers,
            data=post_data
        )

        if response.status_code != 200:
            raise TransportError(f"Server returned unexpected status: {response.status_code}", status_code=response.status_code, content=response.content)

        response_envelope = etree.fromstring(response.content)

        # Notify plugins, that response is received
        for plugin in self.plugins:
            plugin.ingress(response_envelope, http_headers, operation)

        # Check for SOAP Fault
        fault = response_envelope.xpath('/soap12:Envelope/soap12:Body/soap12:Fault', namespaces=builder.namespaces)
        if len(fault) > 0:
            raise Fault(fault[0].xpath('soap12:Reason/soap12:Text/text()', namespaces=builder.namespaces)[0])

        # Check for RegistryResponse Errors
        query_response_status = response_envelope.xpath('/soap12:Envelope/soap12:Body/query:AdhocQueryResponse/@status', namespaces=builder.namespaces)
        if len(query_response_status) > 0 and query_response_status[0] == 'urn:oasis:names:tc:ebxml-regrep:ResponseStatusType:Failure':
            errors = response_envelope.xpath('/soap12:Envelope/soap12:Body/query:AdhocQueryResponse/rs:RegistryErrorList/rs:RegistryError/@codeContext', namespaces=builder.namespaces)
            raise Fault(','.join(errors))

        return etree_to_dict(response_envelope.xpath('/soap12:Envelope/soap12:Body', namespaces=builder.namespaces)[0])


def slot_by_name(obj: dict, name: str):
    for slot in obj.get('Slot', []):
        if slot['@name'] == name:
            return slot
    raise KeyError(f"Slot with name '{name}' not found")


def classification_slot_by_name(obj: dict, name: str):
    for classification in obj.get('Classification', []):
        for slot in classification.get('Slot', []):
            if slot['@name'] == name:
                return slot
    raise KeyError(f"Slot with name '{name}' not found")
