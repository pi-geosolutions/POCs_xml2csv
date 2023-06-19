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

csv_delimiter=';'


def drop_empty_string(list_of_strings, inline=True):
    """
    Drop strings that are empty or just containing spaces from the given list of strings
    :return:
    """
    new_list = [x for x in list_of_strings if x.strip() != '']
    if inline:
        list_of_strings = new_list
    return new_list


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
    pocs_list = set()
    pocs_fields = ("org_name", "role", "email", "ind_name", "ind_position")

    # Scan the xml file and extract the list of valid POCs
    try:
        tree = etree.parse(source_file)
        cit_namespaces = {
                              'cit': 'http://standards.iso.org/iso/19115/-3/cit/2.0',
                              'gco': 'http://standards.iso.org/iso/19115/-3/gco/1.0',
                          }
        pocs = tree.xpath('.//cit:CI_Responsibility', namespaces=cit_namespaces )
        print(f'Reading {len(pocs)} entries from XML file')
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

                pocs_list.add((",".join(drop_empty_string(org_name)),
                    ",".join(drop_empty_string(role)),
                    ",".join(drop_empty_string(email)),
                    ",".join(drop_empty_string(ind_name)),
                    ",".join(drop_empty_string(ind_position)),
                                    ))
    except etree.ParseError as e:
        print(f"Oops, cannot parse {source_file}")
        print(e)

    print(f'Got {len(pocs_list)} distinct results')

    if not pocs_list:
        print(f"List of parsed pocs is empty, there might be an issue")
        return

    # Write the results
    if output_file:
        csv_columns = pocs_fields
        csv_file = output_file
        try:
            with open(csv_file, 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=csv_delimiter, quotechar='"')
                writer.writerow(csv_columns)
                for data in sorted(pocs_list):
                    writer.writerow(data)
        except IOError:
            print("I/O error")
    else:
        # Simply write to stdout
        print('    ----------------------------------------      ')
        print('You did not set an output file. Writing to stdout:')
        print('    ----------------------------------------      ')
        print(csv_delimiter.join(pocs_fields))
        for p in pocs_list:
            print(csv_delimiter.join(p))


if __name__ == '__main__':
    pocs_xml2csv()