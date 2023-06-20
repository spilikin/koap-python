import requests
from rich import print


def test_manual_request():
    # read http body from provide.xop to string
    with open('tests/facade/epa/provide.xop', 'rb') as f:
        body = f.read()
    
    # prepare http request headers
    headers = {
        'Content-Type': 'multipart/related; boundary=_MIME_MTOM_Boundary_; type="application/xop+xml"; start="<Start@Request.konlan>"; start-info="application/soap+xml"; action="urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b"',
        'SOAPAction': 'urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b',
    }

    # send http request, insecure - no certificate verification
    response = requests.post(
        'https://192.168.1.194:443/ws/PHRManagementService', 
        headers=headers, 
        data=body,
        verify=False)

    print(response.text)
  