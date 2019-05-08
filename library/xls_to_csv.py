#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     Copyright (c) 2019 World Wide Technology, Inc.
#     All rights reserved.
#
#     author: joel.king@wwt.com
#     written:  18 April 2019
#     linter: flake8
#         [flake8]
#         max-line-length = 160
#         ignore = E402
#
ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': '@joelwking'
}

DOCUMENTATION = '''
---
module: xls_to_csv.py
author: Joel w, King, World Wide Technology
version_added: "2.9"
short_description: Read an Excel .xlsx file and output .csv files for each sheet specified
description:
    - Read the Excel file specified and output a CSV file for each sheet specified.

requirements:
    - The pandas library ust be installed on the Ansible host. This can be installed using pip:
    -   sudo pip install pandas
    -   sudo pip install xlrd

options:
    src:
        description:
            - The filename of the Excel spreadsheet to read
        required: true

    dest:
        description:
            - The destination directory to write the resulting CSV file(s)
        required: true

    warn:
        description:
            - A boolean to specify if warnings should be issued for sheets found, but skipped
        required: false
        default: false

    sheets:
        description:
            - A list specifying the name(s) of the sheets to retrieve and output
        required: true
'''

EXAMPLES = '''

    Identify the names of the sheets located in the source file, but don't write any output files.

    - xls_to_csv:
        src: '/it-automation-aci/TEST_DATA/WWT_ACI_Constructs_and_Policies.xlsx'
        dest: '/tmp/'
        sheets: []
        warn: True

    Select one or more sheets and write the output to '/tmp/'. The trailing space is optional.

    - xls_to_csv:
        src: '/it-automation-aci/TEST_DATA/WWT_ACI_Constructs_and_Policies.xlsx'
        dest: '/tmp/'
        sheets: 'Tenant-EPG'

    - xls_to_csv:
        src: '/it-automation-aci/TEST_DATA/WWT_ACI_Constructs_and_Policies.xlsx'
        dest: '/tmp'
        sheets:
          - 'Tenant-EPG'
          - 'DHCP Relay'
        warn: True

'''
RETURN = '''
sheet_filenames:
    description: filename of the output .CSV file in the specified destination directory
    returned: always
    type: list
    sample: "TenantEPG"
'''

#
# Constants
#
ERROR = 0
OK = 1
EXTENSION = '.csv'
START_WITH_LETTER = 'Z_'
FACTS = 'ansible_facts'

#
# Imports
#
import csv
import re

from ansible.module_utils.basic import AnsibleModule

try:
    HAS_LIB = True
    import pandas as pd
    # import xlrd                                           # pandas Install xlrd >= 0.9.0 for Excel support
except ImportError:
    HAS_LIB = False


def read_xls(input_file, sheets, warn):
    """
    Read the .xlsx file and load the sheets specified in 'sheets' into a dictionary of facts.
    variable 'warn' specifies if the program should output a warning specifying sheets located
    but not processed.
    """
    result = {FACTS: dict(),
              "warnings": [],
              "changed": False}
    data_frame = dict()                                    # each sheet in the file stored as data frame

    try:
        xlsx = pd.ExcelFile(input_file)
    except IOError:
        return (ERROR, 'IOError on input file:{}'.format(input_file))

    for sheet in xlsx.sheet_names:                         # list of sheet names to extract
        if sheet in sheets:
            data_frame[sheet] = xlsx.parse(sheet)          # read the sheet to a DataFrame
            result[FACTS][get_valid_name(sheet)] = get_rows(data_frame[sheet])
        else:
            if warn:
                result['warnings'].append('sheet "{}" found in source file, skipping'.format(sheet))

    return (OK, result)


def get_valid_name(name):
    """
        Per Ansible https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html
        Variable names should be letters, numbers, and underscores.
        Variables should always start with a letter.

        Remove special characters, spaces, leave underscores

    """
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)

    if name[0].isalpha():
        return name

    return '{}{}'.format(START_WITH_LETTER, name)


def get_rows(data_frame):
    """
    data_frame: a data frame
    return: a list of dictionaries, the key is the column header and the value is the contents of the column

    Note: The column headers `for column in _df['Tenant-EPG'].columns:`
    """
    rows = []

    for row_number, row_content in data_frame.iterrows():  # returns a tuple,  row number and content
        row = {}
        for item in range(0, len(row_content)):
            column_name = get_valid_name(data_frame.columns[item])
            row[column_name] = row_content[item]
        rows.append(row)

    return rows                                            # rows is a list of dictionaries


def write_csv(result, destination_dir):
    """
        Write the requested sheets to the destination directory
    """
    changed = False                                        # Only set 'changed' flag if we write files

    if not destination_dir:
        return (ERROR, 'No output directory specified, nothing to write')

    for sheet in result[FACTS].keys():
        try:
            output_file = '{}/{}{}'.format(destination_dir, sheet, EXTENSION)
            f = open(output_file, 'w')
        except IOError:
            return (ERROR, 'IOError on output file:{}'.format(output_file))

        fieldnames = result[FACTS][sheet][0].keys()        # Column headers
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in result[FACTS][sheet]:
            try:
                writer.writerow(row)
            except UnicodeEncodeError:
                return(ERROR, '{} UnicodeEncodeError:{}'.format(sheet, row))

        f.close()
        changed = True                                     # We wrote a file, set 'changed' flag

    # Overwrite 'ansible_facts' with only the file names
    result[FACTS] = {'sheet_filenames': result[FACTS].keys()}
    result['changed'] = changed

    return (OK, result)


def main():
    """
        Validate args, check for non-standard libraries, call functions to read XLS and write CSV
    """
    module = AnsibleModule(argument_spec=dict(
                src=dict(required=True),
                dest=dict(required=True),
                warn=dict(required=False, type='bool', default=False),
                sheets=dict(required=True, type='list')
             ),
             add_file_common_args=True)

    # Check if we have the necessary libraries, fail gracefully if not
    if not HAS_LIB:
        module.fail_json(msg='The pandas and xlrd Python modules are required, install using: sudo pip install ...')

    # Read the Excel file
    status, result = read_xls(module.params['src'], module.params['sheets'], module.params['warn'])
    if status == ERROR:
        module.fail_json(msg=result)

    # Write sheets to destination directory
    status, result = write_csv(result, module.params.get('dest'))
    if status == ERROR:
        module.fail_json(msg=result)

    module.exit_json(**result)


if __name__ == '__main__':
    """
        Run the program
    """
    main()
