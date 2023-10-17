import base64
import gzip
import xml.etree.ElementTree as ET


b64_str = 'AXAfiwgABwCjZAL/jVLbTgIxEP0V0ne2sLJczGyJgkESECOKvpG6O7Ibty1pu3j5emcREIwPvkx7zsycOZkW+u+qqG3QutzomDWDBquhTkya61XMxvNZvduNevVmxGrOS53KwmiM2Qc61hfwMFjeUqtBXeRJhotKhk7rkSopPE0ntcFwulxc3c3Hs5uYRUFYTaCZ2sUs8359zvmbC1aopM9fgxT5i+Qbl6oq8A3VMwFHuvYE6eV4KO4bYTtqNcJuG/jvHGztaQEjfC6td+SqVKLZ6/QaURgBP6FhYayWCsVQ6hwLUtthuJFJtr1NS0celNQa+IEkcZdkBSaZF9NK84Bg7q10DvVFapFO8mOcLzD3nzIrRKsdnpHpEw5m1otL4701a+AVgAntXcCjybSjokLSctHSE5FR4H/RwL9bdtPFiFzLTX2WqTpRAfB9Aq5l6XSpFO210wF+BA9FP975fpn89EH4P76B+AJBWcqjaQIAAA=='

d = base64.b64decode(b64_str)

l = int.from_bytes(d[0:2], byteorder='big', signed=False)

print(l, len(d))
xml_bytes = gzip.decompress(d[2:2+l])

xml_str = xml_bytes.decode('ISO8859-15')

root = ET.fromstring(xml_str)

ET.indent(root)
print(ET.tostring(root).decode('ISO8859-15'))

print(xml_str)

new_xml_str = '<?xml version="1.0" encoding="ISO-8859-15" standalone="yes"?><UC_PersoenlicheVersichertendatenXML CDM_VERSION="5.2.0" xmlns="http://ws.gematik.de/fa/vsdm/vsd/v5.2"><Versicherter><Versicherten_ID>T026540286</Versicherten_ID><Person><Geburtsdatum>19790525</Geburtsdatum><Vorname>Daniel</Vorname><Nachname>Mustermann</Nachname><Geschlecht>M</Geschlecht><StrassenAdresse><Postleitzahl>46236</Postleitzahl><Ort>Bottrop</Ort><Land><Wohnsitzlaendercode>D</Wohnsitzlaendercode></Land><Strasse>Gustav-Ohm-Str.</Strasse><Hausnummer>77</Hausnummer></StrassenAdresse></Person></Versicherter></UC_PersoenlicheVersichertendatenXML>'

new_xml_bytes = new_xml_str.encode('ISO8859-15')

gzip_bytes = gzip.compress(new_xml_bytes)
new_len = len(gzip_bytes)

new_data = new_len.to_bytes(2, byteorder='big', signed=False)+gzip_bytes

new_b64_str = base64.b64encode(new_data).decode('utf-8')

print(new_b64_str)