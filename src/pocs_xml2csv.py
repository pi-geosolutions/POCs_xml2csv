#!/usr/bin/env python
"""\
Convert points of contact exported from GeoNetwork API (XML data) to a CSV file

Usage: pocs_xml2csv pocs_file.xml
"""

import click
import csv
from lxml import etree

__author__ = "Jean Pommier"
__license__ = "Apache"
__email__ = "jean.pommier@pi-geosolutions.fr"

csv_delimiter = ";"

standards = {
    "iso19115-3": {
        "namespaces": {
            "cit": "http://standards.iso.org/iso/19115/-3/cit/2.0",
            "gco": "http://standards.iso.org/iso/19115/-3/gco/1.0",
        },
        "xpaths": {
            "root": ".//cit:CI_Responsibility",
            "org_name": ".//cit:party/cit:CI_Organisation/cit:name/*/text()",
            "role": ".//cit:role/cit:CI_RoleCode/@codeListValue",
            "email": ".//cit:electronicMailAddress/*/text()",
            "ind_name": ".//cit:CI_Individual/cit:name/*/text()",
            "ind_position": ".//cit:CI_Individual/cit:positionName/*/text()",
            "logo": ".//cit:logo",
        },
    },
    "iso19139": {
        "namespaces": {
            "gmd": "http://www.isotc211.org/2005/gmd",
            "gco": "http://www.isotc211.org/2005/gco",
        },
        "xpaths": {
            "root": ".//gmd:CI_ResponsibleParty",
            "org_name": ".//gmd:organisationName/*/text()",
            "role": ".//gmd:role/gmd:CI_RoleCode/@codeListValue",
            "email": ".//gmd:contactInfo/gmd:CI_Contact/*/gmd:CI_Address/gmd:electronicMailAddress/*/text()",
            "ind_name": ".//gmd:individualName/*/text()",
            "ind_position": ".//gmd:positionName/*/text()",
            "logo": ".//gmd:logo",
        },
    },
}


def drop_empty_string(list_of_strings, inline=True):
    """
    Drop strings that are empty or just containing spaces from the given list of strings
    :return:
    """
    new_list = [x for x in list_of_strings if x.strip() != ""]
    if inline:
        list_of_strings = new_list
    return new_list


@click.command()
@click.argument("source_file")
@click.option("-o", "--output_file", default="", help="Output CSV file")
@click.option("--standard", default="iso19115-3", help="Standard to use (iso19139 / iso 19115-3)")
def pocs_xml2csv(
    source_file,
    output_file,
    standard,
):
    """
    Convert points of contact exported from GeoNetwork API (XML data) to a CSV file
    :param source_file:
    :param output_file:
    :return:
    """
    std = standards.get(standard)
    if std:
        print(f"Looking for POCs encoded in standard {standard}")
    else:
        print(f"Standard {standard} not found. Quitting")
        return
        
    pocs_list = set()
    pocs_fields = ("org_name", "role", "email", "ind_name", "ind_position")

    ns = std.get("namespaces")
    xp = std.get("xpaths")
    # Scan the xml file and extract the list of valid POCs
    try:
        tree = etree.parse(source_file)
        pocs = tree.xpath(xp.get("root"), namespaces=ns)
        print(f"Reading {len(pocs)} entries from XML file")
        for poc in pocs:
            org_name = poc.xpath(xp.get("org_name"), namespaces=ns,
            )
            role = poc.xpath(xp.get("role"), namespaces=ns
            )
            email = poc.xpath(xp.get("email"), namespaces=ns
            )
            ind_name = poc.xpath(xp.get("ind_name"), namespaces=ns
            )
            ind_position = poc.xpath(xp.get("ind_position"), namespaces=ns)
            logo = poc.xpath(xp.get("logo"), namespaces=ns)
            if logo:
                print(
                    f"WARNING: found logo information in record {org_name},{email},{ind_name},{ind_position}. We don't support logos yet"
                )
            # print(f'{org_name},{email}')
            if email:
                pocs_list.add(
                    (
                        ",".join(drop_empty_string(org_name)),
                        ",".join(drop_empty_string(role)),
                        ",".join(drop_empty_string(email)),
                        ",".join(drop_empty_string(ind_name)),
                        ",".join(drop_empty_string(ind_position)),
                    )
                )
    except etree.ParseError as e:
        print(f"Oops, cannot parse {source_file}")
        print(e)

    print(f"Got {len(pocs_list)} distinct results after deduplication")

    if not pocs_list:
        print(f"List of parsed pocs is empty, there might be an issue")
        return

    # Write the results
    if output_file:
        csv_columns = pocs_fields
        csv_file = output_file
        try:
            with open(csv_file, "w") as csvfile:
                writer = csv.writer(csvfile, delimiter=csv_delimiter, quotechar='"')
                writer.writerow(csv_columns)
                for data in sorted(pocs_list):
                    writer.writerow(data)
        except IOError:
            print("I/O error")
    else:
        # Simply write to stdout
        print("    ----------------------------------------      ")
        print("You did not set an output file. Writing to stdout:")
        print("    ----------------------------------------      ")
        print(csv_delimiter.join(pocs_fields))
        for p in pocs_list:
            print(csv_delimiter.join(p))


if __name__ == "__main__":
    pocs_xml2csv()
