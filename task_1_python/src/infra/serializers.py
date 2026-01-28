import json
from xml.etree.ElementTree import Element, SubElement, tostring

def serialize_json(report):
    return json.dumps(report, ensure_ascii=False, indent=2)



def _to_xml(parent: Element, key: str, value) -> None:
    node = SubElement(parent, key)

    if isinstance(value, dict):
        for k, v in value.items():
            _to_xml(node, str(k), v)

    elif isinstance(value, list):
        for item in value:
            item_node = SubElement(node, "item")
            if isinstance(item, (dict, list)):
                _to_xml(item_node, "value", item)
            else:
                item_node.text = str(item)

    else:
        node.text = "" if value is None else str(value)

def serialize_xml(report: dict) -> str:
    root = Element("report")
    for k, v in report.items():
        _to_xml(root, str(k), v)
    return tostring(root, encoding="unicode")
    