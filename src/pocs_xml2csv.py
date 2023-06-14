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


@click.command()
@click.argument('source_file')
@click.option('-o','--output_file', default='', help='Output CSV file')
def pocs_xml2csv(source_file,
                output_file,
                ):
    """
    Convert points of contact exported from GeoNetwork API (XML data) to a CSV file
    :param source_file:
    :param output_file:
    :return:
    """
    pocs_list = []

    # Scan the xml file and extract the list of valid POCs
    try:
        tree = etree.parse(source_file)
        cit_namespaces = {
                              'cit': 'http://standards.iso.org/iso/19115/-3/cit/2.0',
                              'gco': 'http://standards.iso.org/iso/19115/-3/gco/1.0',
                          }
        pocs = tree.xpath('.//cit:CI_Responsibility', namespaces=cit_namespaces )
        for poc in pocs:
            org_name = poc.xpath('.//cit:party/cit:CI_Organisation/cit:name/*/text()', namespaces=cit_namespaces)
            role = poc.xpath('.//cit:role/cit:CI_RoleCode/@codeListValue', namespaces=cit_namespaces)
            email = poc.xpath('.//cit:electronicMailAddress/*/text()', namespaces=cit_namespaces)
            ind_name = poc.xpath('.//cit:CI_Individual/cit:name/*/text()', namespaces=cit_namespaces)
            ind_position = poc.xpath('.//cit:CI_Individual/cit:positionName/*/text()', namespaces=cit_namespaces)
            logo = poc.xpath('.//cit:logo', namespaces=cit_namespaces)
            if (logo):
                print(f"WARNING: found logo information in record {org_name},{email},{ind_name},{ind_position}. We don't support logos yet")
            # print(f'{org_name},{email}')
            if email:
                pocs_list.append({
                    "org_name": ",".join(org_name),
                    "role": ",".join(role),
                    "email": ",".join(email),
                    "ind_name": ",".join(ind_name),
                    "ind_position": ",".join(ind_position),
                })
    except etree.ParseError as e:
        print(f"Oops, cannot parse {source_file}")
        print(e)

    if not pocs_list:
        print(f"List of parsed pocs is empty, there might be an issue")
        return

    # Write the results
    if output_file:
        csv_columns = pocs_list[0].keys()
        csv_file = output_file
        try:
            with open(csv_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in pocs_list:
                    writer.writerow(data)
        except IOError:
            print("I/O error")
    else:
        # Simply write to stdout
        print('    ----------------------------------------      ')
        print('You did not set an output file. Writing to stdout:')
        print('    ----------------------------------------      ')
        print(",".join(pocs_list[0].keys()))
        for p in pocs_list:
            print(",".join(p.values()))


if __name__ == '__main__':
    pocs_xml2csv()