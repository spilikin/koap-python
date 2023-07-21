from lxml.builder import E
from lxml import etree

# define namespace prefixes for better readability
etree.register_namespace('soap12', 'http://www.w3.org/2003/05/soap-envelope')
etree.register_namespace('phrs', 'http://ws.gematik.de/conn/phrs/PHRService/v1.3')
etree.register_namespace('phr', 'http://ws.gematik.de/fa/phr/v1.1')
etree.register_namespace('conn', 'http://ws.gematik.de/conn/ConnectorContext/v2.0')
etree.register_namespace('com', 'http://ws.gematik.de/conn/ConnectorCommon/v5.0')
etree.register_namespace('wa', 'http://www.w3.org/2005/08/addressing')
etree.register_namespace('xdr', 'urn:ihe:iti:xdr:2014')
etree.register_namespace('xdsb', 'urn:ihe:iti:xds-b:2007')
etree.register_namespace('lcm', 'urn:oasis:names:tc:ebxml-regrep:xsd:lcm:3.0')
etree.register_namespace('rs', 'urn:oasis:names:tc:ebxml-regrep:xsd:rs:3.0')
etree.register_namespace('rim', 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0')
etree.register_namespace('query', 'urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0')


def Soap12Envelope(*children, **attrib):
    return E('{http://www.w3.org/2003/05/soap-envelope}Envelope', *children, **attrib)


def Soap12Header(*children, **attrib):
    return E('{http://www.w3.org/2003/05/soap-envelope}Header', *children, **attrib)


def Soap12Body(*children, **attrib):
    return E('{http://www.w3.org/2003/05/soap-envelope}Body', *children, **attrib)


def ContextHeader(*children, **attrib):
    return E('{http://ws.gematik.de/conn/phrs/PHRService/v1.3}ContextHeader', *children, **attrib)


def Context(context: dict):
    return E(
        '{http://ws.gematik.de/conn/ConnectorContext/v2.0}Context',
        E('{http://ws.gematik.de/conn/ConnectorCommon/v5.0}MandantId', context['MandantId']),
        E('{http://ws.gematik.de/conn/ConnectorCommon/v5.0}ClientSystemId', context['ClientSystemId']),
        E('{http://ws.gematik.de/conn/ConnectorCommon/v5.0}WorkplaceId', context['WorkplaceId']),
    )


def RecordIdentifier(*children, **attrib):
    return E('{http://ws.gematik.de/conn/phrs/PHRService/v1.3}RecordIdentifier', *children, **attrib)


def InsurantId(*children, **attrib):
    return E('{http://ws.gematik.de/fa/phr/v1.1}InsurantId', *children, **attrib)


def HomeCommunityId(*children, **attrib):
    return E('{http://ws.gematik.de/fa/phr/v1.1}HomeCommunityId', *children, **attrib)


def Action(*children, **attrib):
    return E('{http://www.w3.org/2005/08/addressing}Action', *children, **attrib)


# <MessageID xmlns="http://www.w3.org/2005/08/addressing">6e2fa9e2-18fb-4071-b796-a49c5fe9a303</MessageID>
def MessageID(*children, **attrib):
    return E('{http://www.w3.org/2005/08/addressing}MessageID', *children, **attrib)


# <ReplyTo xmlns="http://www.w3.org/2005/08/addressing">
def ReplyTo(*children, **attrib):
    return E('{http://www.w3.org/2005/08/addressing}ReplyTo', *children, **attrib)


# <Address>http://www.w3.org/2005/08/addressing/anonymous</Address>
def Address(*children, **attrib):
    return E('{http://www.w3.org/2005/08/addressing}Address', *children, **attrib)


# <To xmlns="http://www.w3.org/2005/08/addressing">https://192.168.1.194:443/ws/PHRManagementService</To>
def To(*children, **attrib):
    return E('{http://www.w3.org/2005/08/addressing}To', *children, **attrib)


# <xdr:homeCommunityBlock xmlns:xdr="urn:ihe:iti:xdr:2014">
def homeCommunityBlock(*children, **attrib):
    return E('{urn:ihe:iti:xdr:2014}homeCommunityBlock', *children, **attrib)


# <xdr:homeCommunityId>urn:oid:1.2.276.0.76.3.1.315.3.3.1.1</xdr:homeCommunityId>
def homeCommunityId(*children, **attrib):
    return E('{urn:ihe:iti:xdr:2014}homeCommunityId', *children, **attrib)


def ProvideAndRegisterDocumentSetRequest(*children, **attrib):
    return E('{urn:ihe:iti:xds-b:2007}ProvideAndRegisterDocumentSetRequest', *children, **attrib)


def SubmitObjectsRequest(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:lcm:3.0}SubmitObjectsRequest', *children, **attrib)


# <rs:RequestSlotList>
def RequestSlotList(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rs:3.0}RequestSlotList', *children, **attrib)


# <rim:Slot name="homeCommunityId">
def Slot(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}Slot', *children, **attrib)


# <rim:ValueList>
def ValueList(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}ValueList', *children, **attrib)


# <rim:Value>urn:oid:1.2.276.0.76.3.1.315.3.3.1.1</rim:Value>
def Value(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}Value', *children, **attrib)


# <rim:RegistryObjectList>
def RegistryObjectList(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}RegistryObjectList', *children, **attrib)


# <rim:RegistryPackage id="submissionset" objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:RegistryPackage" home="urn:oid:1.2.276.0.76.3.1.315.3.3.1.1">
def RegistryPackage(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}RegistryPackage', *children, **attrib)


# <rim:Classification classificationScheme="urn:uuid:a7058bb9-b4e4-4307-ba5b-e3f0ab85e12d" classifiedObject="submissionset" id="author" objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:Classification">
def Classification(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}Classification', *children, **attrib)


# <rim:Name>
def Name(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}Name', *children, **attrib)


# <rim:LocalizedString xml:lang="de-DE" value="Veranlassung durch Patient"/>
def LocalizedString(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}LocalizedString', *children, **attrib)


# <rim:ExternalIdentifier id="patientId" identificationScheme="urn:uuid:6b5aea1a-874d-4603-a4bc-96a0a7b38446" objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:ExternalIdentifier" registryObject="submissionset" value="X110476138^^^&1.2.276.0.76.4.8&ISO">
def ExternalIdentifier(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}ExternalIdentifier', *children, **attrib)


# <rim:Association associationType="urn:oasis:names:tc:ebxml-regrep:AssociationType:HasMember" id="association-0" sourceObject="submissionset" targetObject="DocumentEntry-0">
def Association(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}Association', *children, **attrib)


# <rim:ExtrinsicObject id="DocumentEntry-0" mimeType="application/xml" objectType="urn:uuid:7edca82f-054d-47f2-a032-9b2a5b5186c1" home="urn:oid:1.2.276.0.76.3.1.315.3.3.1.1">
def ExtrinsicObject(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}ExtrinsicObject', *children, **attrib)


# <Document id="DocumentEntry-0">
def Document(*children, **attrib):
    return E('{urn:ihe:iti:xds-b:2007}Document', *children, **attrib)


# <Include xmlns="http://www.w3.org/2004/08/xop/include" href="cid:Document0@PHRService.konlan"/></Document>
def Include(*children, **attrib):
    return E('{http://www.w3.org/2004/08/xop/include}Include', *children, **attrib)


# <query:AdhocQueryRequest xmlns:ns0="urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0" federated="false" startIndex="0" maxResults="-1">
def AdhocQueryRequest(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0}AdhocQueryRequest', *children, **attrib)


# <query:ResponseOption returnType="LeafClass" returnComposedObjects="true"/>
def ResponseOption(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0}ResponseOption', *children, **attrib)


# <ns1:AdhocQuery xmlns:ns1="urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0" id="urn:uuid:958f3006-baad-4929-a4de-ff1114824431" home="urn:oid:1.2.276.0.76.3.1.315.3.3.1.1">
def AdhocQuery(*children, **attrib):
    return E('{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}AdhocQuery', *children, **attrib)