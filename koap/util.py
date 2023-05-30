from typing import List, Tuple
import xml.etree.ElementTree as ET


def element_to_obj(element: ET.Element, single_elements: List[str] = [], collapse_elements: List[Tuple] = []):
    result = {}
    result.update(element.attrib)
    tag = element.tag.split('}')[-1]

    for child in element:
        key = child.tag.split('}')[-1]
        val = element_to_obj(child, single_elements, collapse_elements)
        if key in single_elements:
            result[key] = val
        elif key in result:
            result[key].append(val)
        elif type(val) == str:
            result[key] = val
        else:
            result[key] = [val]

    if len(result.keys()) == 0:
        return element.text

    if element.text is not None:
        result['_text'] = element.text

    for collapse in collapse_elements:
        if collapse[0] == tag:
            return result[key]

    return result