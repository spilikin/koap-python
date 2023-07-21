from rich import print
from lxml import etree
from lxml.builder import E
from koap.client import ConnectorClient, ConnectorConfig
from uuid import uuid4
from datetime import datetime, timedelta


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


def test_builder():
    config = ConnectorConfig()
    conn = ConnectorClient(config)

    phr_service = conn.create_service_client('PHRService', '2.0.1', module="phrs", binding_local_name='PHRService_Binding_Soap12')

    uid_submissionset = f"2.25.{uuid4().int}"
    # encode bytes as decimal string
    uid_document = f"2.25.{uuid4().int}"
    insurant_id = "X110476138"
    home_community_id = "urn:oid:1.2.276.0.76.3.1.315.3.3.1.1"
    action = "urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b"
    messageID = uuid4()
    to = phr_service._binding_options['address']
    authorPerson = "^Özdemir^Simon^^^Freiherr^^^"
    authorRole = "11^^^&1.3.6.1.4.1.19376.3.276.1.5.13&ISO"
    authorInstitution = "Praxis Simon Freiherr ÖzdemirTEST-ONLY^^^^^&1.2.276.0.76.4.188&ISO^^^^1-SMC-B-Testkarte-883110000096089"
    # set to two hours in the past, since the RU has bad time management
    creationTime = (datetime.now() - timedelta(hours=2)).strftime("%Y%m%d%H%M%S%Z")
    documentUri = "hello.txt"
    documentName = "PsSim: Medikationsplan"

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

    el = Soap12Envelope(
        Soap12Header(
          ContextHeader(
                Context(conn.context()),
                RecordIdentifier(
                    InsurantId(root='1.2.276.0.76.4.8', extension=insurant_id),
                    HomeCommunityId(home_community_id)
                ),
          ),
          Action(action),
          MessageID(str(messageID)),
          To(to),
          ReplyTo(
              Address('http://www.w3.org/2005/08/addressing/anonymous')
          ),
          homeCommunityBlock(
              homeCommunityId(home_community_id)
          )
        ),
        Soap12Body(
            ProvideAndRegisterDocumentSetRequest(
                SubmitObjectsRequest(
                    RequestSlotList(
                        Slot(
                            ValueList(
                                Value(home_community_id)
                            ),
                            name="homeCommunityId"
                        )
                    ),
                    RegistryObjectList(
                        RegistryPackage(
                            Slot(
                                ValueList(
                                    Value(creationTime)
                                ),
                                name="submissionTime"
                            ),
                            Classification(
                                Slot(
                                    ValueList(
                                        Value(authorRole)
                                    ),
                                    name="authorRole"
                                ),
                                Slot(
                                    ValueList(
                                        Value(authorPerson),
                                    ),
                                    name="authorPerson"
                                ),
                                Slot(
                                    ValueList(
                                        Value(authorInstitution)
                                    ),
                                    name="authorInstitution"
                                ),
                                classificationScheme="urn:uuid:a7058bb9-b4e4-4307-ba5b-e3f0ab85e12d",
                                classifiedObject="submissionset",
                                id="author",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:Classification"
                            ),
                            Classification(
                                Slot(
                                    ValueList(
                                        Value("1.3.6.1.4.1.19376.3.276.1.5.12")
                                    ),
                                    name="codingScheme"
                                ),
                                Name(
                                    LocalizedString(
                                        value="Veranlassung durch Patient",
                                        **{'{http://www.w3.org/XML/1998/namespace}lang': "de-DE"}
                                    )
                                ),
                                classificationScheme="urn:uuid:aa543740-bdda-424e-8c96-df4873be8500",
                                classifiedObject="submissionset",
                                id="contentType",
                                nodeRepresentation="8",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:Classification"
                            ),
                            Classification(
                                classificationNode="urn:uuid:a54d6aa5-d40d-43f9-88c5-b4633d873bdd",
                                classifiedObject="submissionset",
                                id="SubmissionSetClassification",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:Classification"

                            ),
                            ExternalIdentifier(
                                Name(
                                    LocalizedString(value="XDSSubmissionSet.patientId"),
                                ),
                                id="patientId",
                                identificationScheme="urn:uuid:6b5aea1a-874d-4603-a4bc-96a0a7b38446",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:ExternalIdentifier",
                                registryObject="submissionset",
                                value=f"{insurant_id}^^^&1.2.276.0.76.4.8&ISO"
                            ),
                            ExternalIdentifier(
                                Name(
                                    LocalizedString(value="XDSSubmissionSet.uniqueId"),
                                ),
                                id="uniqueId",
                                identificationScheme="urn:uuid:96fdda7c-d067-4183-912e-bf5ee74998a8",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:ExternalIdentifier",
                                registryObject="submissionset",
                                value=uid_submissionset,
                            ),
                            id="submissionset",
                            objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:RegistryPackage",
                            home="urn:oid:1.2.276.0.76.3.1.315.3.3.1.1"
                        ),
                        Association(
                            Slot(
                                ValueList(
                                    Value("Original")
                                ),
                                name="SubmissionSetStatus"
                            ),
                            associationType="urn:oasis:names:tc:ebxml-regrep:AssociationType:HasMember",
                            id="association-0",
                            sourceObject="submissionset",
                            targetObject="DocumentEntry-0"
                        ),
                        ExtrinsicObject(
                            Slot(
                                ValueList(
                                    Value(creationTime)
                                ),
                                name="creationTime"
                            ),
                            Slot(
                                ValueList(
                                    Value("de-DE")
                                ),
                                name="languageCode"
                            ),
                            Slot(
                                ValueList(
                                    Value(documentUri)
                                ),
                                name="URI"
                            ),
                            Name(
                                LocalizedString(
                                    value=documentName,
                                    **{'{http://www.w3.org/XML/1998/namespace}lang': "de-DE"}
                                )
                            ),
                            Classification(
                                Slot(
                                    ValueList(
                                        Value("1.3.6.1.4.1.19376.3.276.1.5.8")
                                    ),
                                    name="codingScheme"
                                ),
                                Name(
                                    LocalizedString(
                                        value="Planungsdokument",
                                        **{'{http://www.w3.org/XML/1998/namespace}lang': "de-DE"}
                                    )
                                ),
                                classificationScheme="urn:uuid:41a5887f-8865-4c09-adf7-e362475b143a",
                                classifiedObject="DocumentEntry-0",
                                id="class-0",
                                nodeRepresentation="PLA",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:Classification",
                            ),
                            Classification(
                                Slot(
                                    ValueList(
                                        Value("1.2.276.0.76.5.491")
                                    ),
                                    name="codingScheme"
                                ),
                                Name(
                                    LocalizedString(
                                        value="Dokument einer Leistungserbringerinstitution",
                                        **{'{http://www.w3.org/XML/1998/namespace}lang': "de-DE"}
                                    )
                                ),
                                classificationScheme="urn:uuid:f4f85eac-e6cb-4883-b524-f2705394840f",
                                classifiedObject="DocumentEntry-0",
                                id="confidentiality-0",
                                nodeRepresentation="LEI",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:Classification"
                            ),
                            Classification(
                                Slot(
                                    ValueList(
                                        Value("1.3.6.1.4.1.19376.3.276.1.5.6")
                                    ),
                                    name="codingScheme"
                                ),
                                Name(
                                    LocalizedString(
                                        value="Medikationsplan (gematik)",
                                        **{'{http://www.w3.org/XML/1998/namespace}lang': "de-DE"}
                                    )
                                ),
                                classificationScheme="urn:uuid:a09d5840-386c-46f2-b5ad-9c3699a4309d",
                                classifiedObject="DocumentEntry-0",
                                id="formatCode-0",
                                nodeRepresentation="urn:gematik:ig:Medikationsplan:r3.1",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:Classification",
                            ),
                            Classification(
                                Slot(
                                    ValueList(
                                        Value("1.3.6.1.4.1.19376.3.276.1.5.2")
                                    ),
                                    name="codingScheme"
                                ),
                                Name(
                                    LocalizedString(
                                        value="Arztpraxis",
                                        **{'{http://www.w3.org/XML/1998/namespace}lang': "de-DE"}
                                    ),
                                ),
                                classificationScheme="urn:uuid:f33fb8ac-18af-42cc-ae0e-ed0b0bdb91e1",
                                classifiedObject="DocumentEntry-0",
                                id="healthCare-0",
                                nodeRepresentation="PRA",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:Classification"
                            ),
                            Classification(
                                Slot(
                                    ValueList(
                                        Value("11^^^&1.3.6.1.4.1.19376.3.276.1.5.13&ISO")
                                    ),
                                    name="authorRole"
                                ),
                                Slot(
                                    ValueList(
                                        Value(authorPerson)
                                    ),
                                    name="authorPerson"
                                ),
                                classificationScheme="urn:uuid:93606bcf-9494-43ec-9b4e-a7748d1a838d",
                                classifiedObject="DocumentEntry-0",
                                id="author-0",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:Classification",
                            ),
                            Classification(
                                Slot(
                                    ValueList(
                                        Value("1.3.6.1.4.1.19376.3.276.1.5.4")
                                    ),
                                    name="codingScheme"
                                ),
                                Name(
                                    LocalizedString(
                                        value="Allgemeinmedizin",
                                        **{'{http://www.w3.org/XML/1998/namespace}lang': "de-DE"}
                                    ),
                                ),
                                classificationScheme="urn:uuid:cccf5598-8b07-4b77-a05e-ae952c785ead",
                                classifiedObject="DocumentEntry-0",
                                id="practiceSettingCode-0",
                                nodeRepresentation="ALLG",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:Classification"
                            ),
                            Classification(
                                Slot(
                                    ValueList(
                                        Value("1.3.6.1.4.1.19376.3.276.1.5.9")
                                    ),
                                    name="codingScheme"
                                ),
                                Name(
                                    LocalizedString(
                                        value="Medikamentöse Therapien",
                                        **{'{http://www.w3.org/XML/1998/namespace}lang': "de-DE"}
                                    ),
                                ),
                                classificationScheme="urn:uuid:f0306f51-975f-434e-a61c-c59651d33983",
                                classifiedObject="DocumentEntry-0",
                                id="typeCode-0",
                                nodeRepresentation="MEDI",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:Classification"
                            ),
                            ExternalIdentifier(
                                Name(
                                    LocalizedString(
                                        value="XDSDocumentEntry.patientId",
                                    ),
                                ),
                                id="patientId-0",
                                identificationScheme="urn:uuid:58a6f841-87b3-4a3e-92fd-a8ffeff98427",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:ExternalIdentifier",
                                registryObject="DocumentEntry-0",
                                value="X110476138^^^&1.2.276.0.76.4.8&ISO"
                            ),
                            ExternalIdentifier(
                                Name(
                                    LocalizedString(
                                        value="XDSDocumentEntry.uniqueId",
                                    ),
                                ),
                                id="uniqueId-0",
                                identificationScheme="urn:uuid:2e82c1f6-a085-4c72-9da3-8640a32e42ab",
                                objectType="urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:ExternalIdentifier",
                                registryObject="DocumentEntry-0",
                                value=uid_document
                            ),
                            
                            id="DocumentEntry-0",
                            mimeType="application/xml",
                            objectType="urn:uuid:7edca82f-054d-47f2-a032-9b2a5b5186c1",
                            home=home_community_id
                        ),
                    ),
                ),
                Document(
                    Include(
                        href="cid:Document0@PHRService.konlan"
                    ),
                    id="DocumentEntry-0",
                ),

            ),
        ),
    )

    print(etree.tostring(el, pretty_print=True).decode())

    # read template from file
    with open("tests/facade/epa/provide.xop.template", "rb") as f:
        tmpl = f.read().decode()

    message = tmpl.replace("{{envelope}}", etree.tostring(el, pretty_print=True).decode())

    # write message to xop file
    with open("tests/facade/epa/provide.xop", "wb") as f:
        f.write(message.encode())

    # write message only to xml file
    with open("tests/facade/epa/message.xml", "wb") as f:
        f.write(etree.tostring(el, pretty_print=True))

    # read message from file
    with open("tests/facade/epa/message.xml", "rb") as f:
        message = etree.fromstring(f.read())

    # read reference message from file
    with open("tests/facade/epa/message-working.xml", "rb") as f:
        message_working = etree.fromstring(f.read())

    def compare_el(e1: etree._Element, e2: etree._Element):
        #print(e1.tag, e2.tag)
        assert e1.tag == e2.tag
            
        #print(e1.attrib, e2.attrib)
        #assert e1.attrib == e2.attrib
        # iterate all children and compare them too
        # filter comments out
        children1 = [c for c in e1 if not isinstance(c, etree._Comment)]
        children2 = [c for c in e2 if not isinstance(c, etree._Comment)]
        for c1, c2 in zip(children1, children2):
            compare_el(c1, c2)

        # compare text
        if e1.text != e2.text:
            print(f"{e1.tag} {e1.text} != {e2.text}")

    compare_el(message, message_working)


