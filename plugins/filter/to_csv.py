# -*- coding: utf-8 -*-
#
#     Copyright (c) 2020 World Wide Technology
#     All rights reserved.
#
#     GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
#     author: joel.king@wwt.com
#     written:  16 December 2020
#     linter: flake8
#         [flake8]
#         max-line-length = 160
#         ignore = E402
#


def do_to_csv(value):
    """
    Input is a list of dictionaries. Each list item is converted to a row (line) of the CSV file
    the dictionary keys are inserted before the first record, representing the column headers.
    Output is a string with newline characters. This string can be written to a file and opened
    with Excel or other program which recognizes CSV file formats.

    """
    headers = value[0].keys()                              # Get the keys from the first record
    hdr = dict()                                           # The first record in a CSV file are the column headers
    for item in headers:
        hdr[item] = item                                   # make the value of the key the text of the column header

    value.insert(0, hdr)                                   # insert text of the column headers as the first record

    table = ""                                             # create an empty string, which will be returned to the caller

    for item in value:
        row = ''                                           # create an empty row
        for column in headers:
            if len(item[column]) == 0:                     # for empty fields, return a space
                item[column] = ' '
            row += item[column] + ','                      # add the column to the row and a comma as a delimiter

        table += "{}\n".format(row[:-1])                   # remove the trailing delimiter and the row and newline

    return table


class FilterModule(object):
    """
        Filter to create CSV formatted output
    """

    def filters(self):
        filters = {
            'to_csv': do_to_csv,
        }

        return filters
