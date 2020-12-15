# -*- coding: utf-8 -*-
#
#     Copyright (c) 2020 World Wide Technology
#     All rights reserved.
#
#     GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
#     author: joel.king@wwt.com
#     written:  18 April 2019
#     linter: flake8
#         [flake8]
#         max-line-length = 160
#         ignore = E402
#
"""
try:
    from jinja2.filters import do_urlencode
    HAS_URLENCODE = True
except ImportError:
    HAS_URLENCODE = False
"""


def do_to_csv(value):
    
    headers = value[0].keys()              # Get the keys from the first record
    hdr = dict()
    for item in headers:
      hdr[item] = item

    value.insert(0, hdr)
    table = ""

    for item in value:
        row = ''
        for column in headers:
            if len(item[column]) == 0:
                item[column] = ' '
            row += item[column] + ','

        table += "{}\n".format(row[:-1])

    return table


class FilterModule(object):
    """
        Filter to create CSV format
    """

    def filters(self):
        filters = {
            'to_csv': do_to_csv,
        }

        return filters