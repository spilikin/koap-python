from koap.client import ConnectorClient
from pydantic import BaseModel
from koap.facade.model import CardTypeEnum
from koap.facade.model import obj_to_card, Card, CARD_TYPES_SMCB
from typing import Tuple, List
import datetime
from lxml import etree
import xmltodict
from . import builder
from uuid import uuid4


SOAP_ACTION_REGISTRY_STORED_QUERY = "urn:ihe:iti:2007:RegistryStoredQuery"
SOAP_ACTION_RETRIEVE_DOCUMENT_SET = "urn:ihe:iti:2007:RetrieveDocumentSet"
SOAP_ACTION_PROVIDE_AND_REGISTER_DOCUMENT_SET_B = "urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b"
SOAP_ACTION_DELETE_DOCUMENT_SET = "urn:ihe:iti:2010:DeleteDocumentSet"


# very quick and dirty hack to remove the namespace prefix and convert to dict
def etree_to_dict(el: etree.ElementBase):
    for el2 in el.findall('.//*'):
        # if element namespace is urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0, remove the ns prefix
        if el2.tag.startswith('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}'):
            el2.tag = el2.tag.split('}', 1)[1]

    as_dist = xmltodict.parse(etree.tostring(el, encoding='utf8', method='xml', pretty_print=True))

    # get the value of the fist entry in dict
    as_dist = as_dist[list(as_dist.keys())[0]]

    return as_dist


class InsurantId(BaseModel):
    extension: str
    root: str = "1.2.276.0.76.4.8"


class RecordId(BaseModel):
    HomeCommunityId: str
    InsurantId: str


class EPAFacade:
    def __init__(self, client: ConnectorClient):
        self.client = client
        self.phr_mgt_service = client.create_service_client('PHRManagementService', '2.0.1', module="phrs")
        self.phr_service = client.create_service_client('PHRService', '2.0.1', module="phrs", binding_local_name='PHRService_Binding_Soap12')
        self.event_service = client.create_service_client('EventService', '7.2.0')

    def get_home_community_id(self, kvnr: str):
        response = self.phr_mgt_service.GetHomeCommunityID(
            Context=self.client.context(),
            InsurantID=InsurantId(extension=kvnr).dict(),
        )
        # TODO: camelcase ID
        return response['HomeCommunityID']

    def get_authorization_list(self):
        response = self.phr_mgt_service.GetAuthorizationList(
            Context=self.client.context(),
        )
        return response['AuthorizationList']['_value_1']

    def get_cards(self) -> Tuple[List[Card], List[Card]]:
        get_cards_response = self.event_service.GetCards(
            Context=self.client.context()
        )
        raw_egks = filter(lambda c: c.CardType in [CardTypeEnum.EGK], get_cards_response.Cards.Card)
        raw_smcbs = filter(lambda c: c.CardType in CARD_TYPES_SMCB, get_cards_response.Cards.Card)
        return list(map(obj_to_card, raw_egks)), list(map(obj_to_card, raw_smcbs))

    def request_facility_authorization(
            self,
            egk: Card,
            smcb: Card,
            record_id: RecordId,
            categories: List[str],
            expiration_date: datetime.date
            ):
        response = self.phr_mgt_service.RequestFacilityAuthorization(
            Context=self.client.context(),
            EhcHandle=egk.CardHandle,
            # TODO: woher weiss man das?
            AuthorizationConfiguration={
                'AuthorizationConfidentiality': 'normal',
                'DocumentCategoryList': {
                    '_value_1': list(map(lambda c: {'DocumentCategoryElement': c}, categories)),
                },
                # TODO: set date
                'ExpirationDate': expiration_date
            },
            RecordIdentifier=record_id.dict(),
            OrganizationName=smcb.CardHolderName,
            # TODO: Vorname und Nachname: Deutsch(!) wo kommt das her? 
            InsurantName={"Vorname": egk.CardHolderName, "Nachname": egk.CardHolderName},
        )
        return response

    def get_authorization_state(self, record_id: RecordId):
        response = self.phr_mgt_service.GetAuthorizationState(
            Context=self.client.context(),
            RecordIdentifier=record_id.dict(),
            # TODO: get koap name and version
            UserAgent="koap/0.1.0/spilikin",
        )
        return response


class EPARecordFacade:
    def __init__(self, epa_facade: EPAFacade, record_id: RecordId):
        self.epa_facade = epa_facade
        self.record_id = record_id

    def get_folders(self):
        session = self.epa_facade.client.transport.session
        # get endpoint url from zeep
        address = self.epa_facade.phr_service._binding_options['address']

        headers = {
            'Content-Type': f'application/soap+xml; charset=utf-8; action="{SOAP_ACTION_REGISTRY_STORED_QUERY}"',
            'SOAPAction': SOAP_ACTION_REGISTRY_STORED_QUERY,
        }

        messageID = uuid4()
        to = address

        message = builder.Soap12Envelope(
            builder.Soap12Header(
                builder.ContextHeader(
                        builder.Context(self.epa_facade.client.context()),
                        builder.RecordIdentifier(
                            builder.InsurantId(root='1.2.276.0.76.4.8', extension=self.record_id.InsurantId),
                            builder.HomeCommunityId(self.record_id.HomeCommunityId)
                        ),
                ),
                builder.Action(SOAP_ACTION_REGISTRY_STORED_QUERY),
                builder.MessageID(str(messageID)),
                builder.To(to),
                builder.ReplyTo(
                    builder.Address('http://www.w3.org/2005/08/addressing/anonymous')
                ),
                builder.homeCommunityBlock(
                    builder.homeCommunityId(self.record_id.HomeCommunityId)
                )
            ),
            builder.Soap12Body(
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
                                builder.Value(f"('{self.record_id.InsurantId}^^^&amp;1.2.276.0.76.4.8&amp;ISO')")
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
        )

        operation = self.epa_facade.phr_service._binding._operations['DocumentRegistry_RegistryStoredQuery']

        if len(self.epa_facade.client.soap_plugins) > 0:
            plugin = self.epa_facade.client.soap_plugins[0]
            plugin.egress(message, headers, operation, None)

        body = etree.tostring(message, pretty_print=True).decode()

        response = session.post(
            address,
            headers=headers,
            data=body
        )

        if response.status_code != 200:
            raise Exception(f"Server returned unexpected status: {response.status_code}")

        response_envelope = etree.fromstring(response.content)

        if len(self.epa_facade.client.soap_plugins) > 0:
            plugin = self.epa_facade.client.soap_plugins[0]
            plugin.ingress(response_envelope, headers, operation)

        nsmap = {
            'soap12': 'http://www.w3.org/2003/05/soap-envelope',
            'rs': 'urn:oasis:names:tc:ebxml-regrep:xsd:rs:3.0',
            'query': 'urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0'
        }
        fault = response_envelope.xpath('/soap12:Envelope/soap12:Body/soap12:Fault', namespaces=nsmap)

        if len(fault) > 0:
            # TODO: make proper exception
            raise Exception(fault[0].xpath('soap12:Reason/soap12:Text/text()', namespaces=nsmap)[0])

        query_response = response_envelope.xpath('/soap12:Envelope/soap12:Body/query:AdhocQueryResponse', namespaces=nsmap)[0]

        if query_response.get('status') == 'urn:oasis:names:tc:ebxml-regrep:ResponseStatusType:Failure':
            errors = query_response.xpath('rs:RegistryErrorList/rs:RegistryError/@codeContext', namespaces=nsmap)
            raise Exception(','.join(errors))

        return etree_to_dict(query_response)
