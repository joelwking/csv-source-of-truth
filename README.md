# csv-source-of-truth
Collection of modules and documentation to enable using Microsoft Excel (and CSV files) as a Source of Truth

## Overview
The goal of this effort is to enable using a on-line or local spreadsheet program (Microsoft Excel) to define the configuration of a network fabric, in our use case, Cisco Application Centric Infrastructure (ACI).

Microsoft Excel is readily available, provides a high degree of functionality for data visualization and analysis, and is commonly used by network engineers for the definition of data center fabrics.

While YAML is a human-readable data serialization language and perhaps more suitable, especially given using Ansible as a configuration management tool, the whitespace indentation to provide structure can be confusing initially to the non-programmer.

## Challenges

### Data Structure
Spreadsheets represent data in a similar format to a relational database. The database stores data in objects called tables, which consist of columns and rows. The columns include a column name and other attributes.

The spreadsheet file (.xlsx) is analogous to a database, while one or more *sheets* in the file are analogous to tables in the database. 

In our use case, configuring a Cisco ACI fabric, the Cisco Application Policy Infrastructure Controller (Cisco APIC) manages the model of the ACI fabric in a hierarchical (tree) structure. At the top of the tree structure is the root (*topRoot*) and the policy Universe (*polUni*) is contained by topRoot. 

The challenge in using a spreadsheet to represent the configuration of the ACI fabric focuses on optimizing and eliminating redundancy in a flat structure of the sheet to a hierarchal structure of the APIC Management Information Tree (MIT). 

### Elimination of Manual Operations
dddd

### Naming Requirement

### Data Types
