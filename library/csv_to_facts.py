#!/usr/bin/env python
#
#     Copyright (c) 2019 World Wide Technology, Inc. All rights reserved.
#     GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': '@joelwking'
}

DOCUMENTATION = '''
---
module: csv_to_facts
short_description: Reads a CSV file and returns as ansible facts a list of dictionaries for each row

version_added: "2.8"

description:
    - Reads the CSV file specified and output Ansible facts in the form of a list with each
    - element in the list as a dictionary. The column header is used as the key and the contents
    - of the cell as the value. Also returns a dictionary with each column header as a key, the
    - value is a list of unique values for the column, a set.

options:
    src:
        description:
            - The CSV formatted input file
        required: true
        type: str

    table:
        description:
            - The name of the list created.
        required: false
        default: 'spreadsheet'
        type: str

    vsheets:
        description:
            - A list of dictionaries. The key is the namespace to store the results, the values
            - are the fields to select from the spreadsheet, creating a virtual spreadsheet with
            - using the fields specified. Defaults to empty list.
        required: false
        type: list
        default: []

author:
    - Joel W. King (@joelwking)
'''

EXAMPLES = '''

    Given an input CSV file:

    appliance,name,address,partition,port
    10.255.138.87,NEW_NODE1,192.0.2.1,Common,80
    10.255.138.87,NEW_NODE2,198.51.100.1,Common,80
    10.255.138.87,NEW_NODE1,192.0.2.1,Common,443

    tasks:
    - name: Get facts from CSV file
      csv_to_facts:
        src: '{{ ifile }}'
        table: f5
        vsheets:
          - NAMEs:
              - name
          - LISTENERs:
              - address
              - port

    returns:

    "ansible_facts": {
        "LISTENERs": [
            {
                "address": "192.0.2.1",
                "port": "443"
            },
            {
                "address": "198.51.100.1",
                "port": "80"
            },
            {
                "address": "192.0.2.1",
                "port": "80"
            }
        ],
        "NAMEs": [
            {
                "name": "NEW_NODE1"
            },
            {
                "name": "NEW_NODE2"
            }
        ],
               "f5": [
            {
                "address": "192.0.2.1",
                "appliance": "10.255.138.87",
                "name": "NEW_NODE1",
                "partition": "Common",
                "port": "80"
            },
            and so on....
'''

import csv
from ansible.module_utils.basic import AnsibleModule

ERROR = 1
OK = 0


class virt_spreadsheet(object):
    """
        Given a spreadsheet, we take each name and values entered as arguments, and
        create a virtual spreadsheet.
        Sample input
          name: 'VRFs'
          values: ['Tenant', 'VRF']
          spreadsheet: a list of dictionaries
    """
    def __init__(self, name, values, spreadsheet):

        self.name = name
        self.values = values
        self.spreadsheet = spreadsheet
        self.virt_set = set()
        self.virt_sheet = []
        self.error = None

    def populate_sheet(self):
        """ Populate the virtual spreadsheet from the main sheet, using the name and values
            requested in the playbook.
        """
        for row in self.spreadsheet:                       # Loop thru main spreadsheet
            virt_row = {}
            for column_header in self.values:              # create virtual row for the user requested columns
                try:
                    virt_row[column_header] = row[column_header]
                except KeyError:
                    self.error = 'column requested, "{}", does not exist'.format(column_header)

            self.virt_set.add(tuple(virt_row.items()))    # convert to a tuple allowing the 'set' to drop duplicates
        for item in self.virt_set:                        # convert the set back to a dictionary
            self.virt_sheet.append(dict(item))            # self.virt_sheet is the new virtual spreadsheet
        return                                            # self.error is None or contains an error message


def read_csv_dict(input_file, table_name, vsheets):
    """
        Read the input file, create a list of dictionaries. Each list element is a row, each row is a dictionary
        with the key being the column header, and the value the contents of the cell. The table_name is input
        by the user, it defaults to 'spreadsheet'.

        Optionally, create any number of virtual spreadsheets from the main spreadsheet, which represents selected
        columns from the main spreadsheet, comprised of unique values from the main spreadsheet.
    """

    result = {"ansible_facts": {}}
    spreadsheet = {table_name: [],
                   # vsheet name(s): [],
                   # vsheet name2: []
                   }
    #
    # Read file and create main spreadsheet
    #
    try:
        with open(input_file) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                spreadsheet[table_name].append(row)
    except IOError:
        return (ERROR, "IOError on input file:%s" % input_file)
    csvfile.close()
    #
    # Optionally create virtual spreadsheets with a unique row for the values
    #
    for item in vsheets:
        if len(item) is not 1:
            return(ERROR, "only one virtual sheet name per item")

        ovs = virt_spreadsheet(item.keys()[0], item[item.keys()[0]], spreadsheet[table_name])
        ovs.populate_sheet()
        if ovs.error:
            return(ERROR, ovs.error)
        spreadsheet[ovs.name] = ovs.virt_sheet             # add the virtual sheet set to the results
    #
    # Store the entire file as a list of dictionaries in the table name (and virtual sheet names) requested
    #
    result["ansible_facts"] = spreadsheet
    return (OK, result)


def main():
    """
    MAIN: manage areguments and error checking, exit or fail as appropriate
    """
    module = AnsibleModule(argument_spec=dict(
                 src=dict(required=True, type='str'),
                 table=dict(default='spreadsheet', required=False, type='str'),
                 vsheets=dict(default=[], required=False, type='list')
                 ),
                 add_file_common_args=True)

    if module.params["vsheets"] is None:                   # argument "vsheets" specified, but with no data
        module.params["vsheets"] = []                      # rather than error, set as null list and continue

    code, response = read_csv_dict(module.params["src"],
                                   module.params["table"],
                                   module.params["vsheets"])
    if code == ERROR:
        module.fail_json(msg=response)
    else:
        module.exit_json(**response)

    return code


main()
