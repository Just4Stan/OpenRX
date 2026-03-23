#!/usr/bin/env python3
from __future__ import annotations

import csv
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path


def comp_fields(comp: ET.Element) -> dict[str, str]:
    fields: dict[str, str] = {}
    fields_el = comp.find("fields")
    if fields_el is None:
        return fields
    for field in fields_el.findall("field"):
        name = field.get("name", "").strip()
        if name:
            fields[name] = (field.text or "").strip()
    return fields


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: export_grouped_lcsc_bom.py INPUT_XML OUTPUT_CSV", file=sys.stderr)
        return 2

    input_xml = Path(sys.argv[1])
    output_csv = Path(sys.argv[2])

    root = ET.parse(input_xml).getroot()
    comps_el = root.find("components")
    if comps_el is None:
        raise SystemExit(f"no <components> in {input_xml}")

    groups: "OrderedDict[tuple[str, ...], dict[str, object]]" = OrderedDict()

    for comp in comps_el.findall("comp"):
        ref = comp.get("ref", "").strip()
        value = (comp.findtext("value") or "").strip()
        footprint = (comp.findtext("footprint") or "").strip()
        datasheet = (comp.findtext("datasheet") or "").strip()
        fields = comp_fields(comp)
        lcsc = fields.get("LCSC", "")
        lcsc_part = fields.get("LCSC Part", "")
        dnp = fields.get("DNP", "")

        key = (value, footprint, lcsc, lcsc_part, datasheet, dnp)
        if key not in groups:
            groups[key] = {
                "refs": [],
                "value": value,
                "footprint": footprint,
                "lcsc": lcsc,
                "lcsc_part": lcsc_part,
                "datasheet": datasheet,
                "dnp": dnp,
            }
        groups[key]["refs"].append(ref)

    with output_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "#",
                "Reference",
                "Qty",
                "Value",
                "Footprint",
                "LCSC",
                "LCSC Part",
                "Datasheet",
                "DNP",
            ]
        )
        for idx, group in enumerate(groups.values(), start=1):
            refs = group["refs"]
            writer.writerow(
                [
                    idx,
                    ", ".join(refs),
                    len(refs),
                    group["value"],
                    group["footprint"],
                    group["lcsc"],
                    group["lcsc_part"],
                    group["datasheet"],
                    group["dnp"],
                ]
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
