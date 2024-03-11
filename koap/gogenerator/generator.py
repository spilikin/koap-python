from zeep.xsd.elements.element import Element
from zeep.xsd.elements import Attribute
from typing import Mapping, List, Set
from zeep.xsd.types import ComplexType
from zeep.xsd.elements import Sequence, Choice
from zeep.xsd.elements.any import Any
from zeep import Client, Settings
from datetime import datetime
import os
from urllib.parse import urlparse
import logging
import re
from os import path
from importlib import resources

shortnames = {
  "urn:oasis:names:tc:dss:1.0:core:schema": "ext/dss10core",
  "urn:oasis:names:tc:dss-x:1.0:profiles:verificationreport:schema#": "ext/dssx10verificationreport",
  "http://www.w3.org/2000/09/xmldsig#": "ext/xmldsig",
  "http://uri.etsi.org/02231/v2#": "ext/etsi02232v2",
  "http://uri.etsi.org/01903/v1.3.2#": "ext/etsi01903v132",
}


class GoGenerator:
    def __init__(self, dest: str, package: str):
        self.dest = dest
        self.package = package
        os.makedirs(dest, exist_ok=True)

    types: Mapping[str, Mapping[str, Element]] = {}

    def scan_for_wsdl(self):
        wsdl_files = resources.files("koap") / "api-telematik" / "conn"
        # we make use of gematik naming conventions:
        # - the wsdl file name is the service name
        # - if wsdl file name has vX_Y_Z.wsdl, then the service version is vX.Y.Z
        # - if no version is pecified in the wsdl file name, then the service version taken from targetNamespace. Patch level is 0
        for wsdl_file in wsdl_files.glob("*.wsdl"):
            service_name = wsdl_file.stem
            match = re.match(r"^([^\_]+)_v(\d+_\d+_\d+)$", service_name, re.IGNORECASE)
            if match:
                service_name = match.group(1)
                service_version = match.group(2).replace("_", ".")
            else:
                soap_settings = Settings()
                soap_settings.forbid_entities = False
                client = Client(wsdl=str(wsdl_file), settings=soap_settings)
                _, binding = list(client.wsdl.bindings.items())[0]
                namespace = binding.name.namespace
                service_version = namespace.split("/")[-1].replace("v", "") + ".0"

            self.add_service(wsdl_file, service_name, service_version)

    def add_service(
        self,
        wsdl_file: str,
        service_name: str,
        service_version: str,
    ):

        soap_settings = Settings()
        soap_settings.forbid_entities = False

        client = Client(
            wsdl=str(wsdl_file),
            settings=soap_settings,
        )

        for svc in client.wsdl.services.values():
            for port in svc.ports.values():
                for op in port.binding.all().values():
                    self.add_type(op.abstract.input_message.parts["parameter"].element)
                    self.add_type(op.abstract.output_message.parts["parameter"].element)

    def add_type(self, element: Element):
        ns = element.qname.namespace
        name = element.qname.localname
        if ns not in self.types:
            self.types[ns] = {}

        if name in self.types[ns]:
            # already added
            return

        self.types[ns][name] = element
        if isinstance(element.type, ComplexType):
            for child in self._iterate_children(element):
                if isinstance(child, Element) and isinstance(child.type, ComplexType):
                    self.add_type(child)
                else:
                    logging.warning(
                        f"Skipping unknown {type(child)} {child}"
                    )
        else:
            logging.warning(
                f"Not complex type {type(element.type)} {element.type}"
            )

    # given a namespace, return a list of paths to the types in that namespace
    def paths(self, ns: str) -> List[str]:
        if ns in shortnames:
            ns = shortnames[ns]
        # parse url
        url = urlparse(ns)
        # split path
        paths = url.path.split("/")
        # remove empty elements
        paths = [p for p in paths if p]
        # if last path is semantic version, join it with the previous path
        if re.match(r"v\d+\.\d+(\.\d+)?", paths[-1]):
            paths[-2] = paths[-2] + "_" + paths[-1].replace(".", "_")
            paths = paths[:-1]
        # ist last path starts with number, prepend x to it
        if re.match(r"^\d", paths[-1]):
            paths[-1] = "x" + paths[-1]

        return paths

    def generate_all_types(self):
        for ns, types in self.types.items():
            paths = self.paths(ns)
            dest_dir = path.join(self.dest, *paths)
            self.generate_complextypes(dest_dir, types.values())

    def generate_complextypes(self, dest_dir: str, elements: List[Element]):
        os.makedirs(dest_dir, exist_ok=True)
        elements = sorted(elements, key=lambda e: e.qname.localname)

        file_imports = set()
        file_imports.add("encoding/xml")

        file_code = ""
        for element in elements:
            if isinstance(element.type, ComplexType):
                code, imports = self._element_to_struct(element)
                file_code += code
                file_code += "\n"
                file_imports.update(imports)

        dest_file = path.join(dest_dir, "types.gen.go")
        if file_code == "":
            # do not generate empty files
            return
        with open(dest_file, "w") as f:
            f.write("package " + path.basename(dest_dir) + "\n\n")
            f.write("import (\n")
            for imp in file_imports:
                f.write(f'    "{imp}"\n')
            f.write(")\n\n")
            f.write(file_code)

    def generate_all(self):
        self.generate_all_types()

    def _iterate_children(self, element: ComplexType):
        for name, child in element.type.elements_nested:
            if isinstance(child, Sequence) or isinstance(child, Choice):
                # TODO: handle sequence and choice
                processed = set()
                for name, grandchild in child.elements:
                    if isinstance(grandchild, Any):
                        continue
                    if grandchild.qname in processed:
                        continue
                    processed.add(grandchild.qname)
                    yield grandchild
            elif isinstance(child, Element):
                yield child
            else:
                logging.warning(f"Unknown type: {type(child)} in {element.type}")

    def _element_to_struct(self, element: ComplexType) -> tuple[str, Set[str]]:
        imports = set()
        s = f"type {element.name} struct {{\n"
        s += f'XMLName        xml.Name `xml:"{element.qname.namespace} {element.qname.localname}"`\n'

        for _, attr in element.type.attributes:
            opts = ",attr"

            if not isinstance(attr, Attribute):
                logging.warning(f"Skipping {type(attr)}: {attr}")
                continue

            go_field = self._go_field(attr.qname.localname)
            go_type, imp = self._go_type_of(element, attr)
            if imp is not None:
                imports.add(imp)
            s += f'    {go_field} {go_type} `xml:"{attr.qname.localname}{opts}"`\n'

        for child in self._iterate_children(element):
            opts = ""
            if isinstance(child, Any):
                continue
                
            element_name = f"{child.qname.namespace} {child.qname.localname}"
            go_field = self._go_field(child.qname.localname)
            if child.qname.localname == "_value_1":
                go_field = "Value"
                element_name = ""
                opts = ",chardata"

            go_type, imp = self._go_type_of(element, child)
            # see if go type is from another package (contains .)
            if imp is not None:
                imports.add(imp)
            if child.min_occurs == 0:
                opts += ",omitempty"
            if child.max_occurs == "unbounded" or int(child.max_occurs) > 1:
                go_type = "[]" + go_type
            s += f'    {go_field} {go_type} `xml:"{element_name}{opts}"`\n'
        s += "}\n"

        return s, imports

    def _go_type_of(self, parent: Element, child: Element) -> tuple[str, str]:
        if isinstance(child.type, ComplexType):
            if parent.qname.namespace == child.qname.namespace:
                return child.qname.localname, None
            else:
                paths = self.paths(child.qname.namespace)
                return paths[
                    -1
                ] + "." + child.qname.localname, self.package + "/" + "/".join(paths)
        elif len(child.type.accepted_types) > 0:
            pyt = child.type.accepted_types[0]
            if pyt == str:
                return "string", None
            elif pyt == int:
                return "int", None
            elif pyt == float:
                return "float64", None
            elif pyt == bool:
                return "bool", None
            elif pyt == datetime:
                return "time.Time", "time"
            else:
                return "interface{}", None
        else:
            return "interface{}", None

    def _go_field(self, localname: str):
        # convert snake case to camel case
        parts = localname.split("_")
        localname = parts[0] + "".join(x.title() for x in parts[1:])
        parts = localname.split("-")
        localname = parts[0] + "".join(x.title() for x in parts[1:])
        remove = re.compile(r"[^a-zA-Z0-9_]")
        localname = remove.sub("", localname)
        return localname[0].upper() + localname[1:]
