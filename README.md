# csv-source-of-truth
Collection of modules and documentation to enable using Microsoft Excel (and CSV files) as a Source of Truth

## Overview
The goal of this effort is to enable using a on-line or local spreadsheet program (Microsoft Excel) to define the configuration of a network fabric, in our use case, Cisco Application Centric Infrastructure (ACI).

Microsoft Excel is readily available, provides a high degree of functionality for data visualization and analysis, and is commonly used by network engineers for the definition of data center fabrics.

While YAML is a human-readable data serialization language and perhaps more suitable, especially given using Ansible as a configuration management tool, the whitespace indentation to provide structure can be confusing initially to the non-programmer.

## Challenges

### Data Structure
Spreadsheets represent data in a tabular data format similar to a relational database. The database stores data in objects called tables, which consist of columns and rows. The columns include a column name and other attributes.

The spreadsheet file (.xlsx) is analogous to a database, while one or more *sheets* in the file are analogous to tables in the database. 

In our use case, configuring a Cisco ACI fabric, the Cisco Application Policy Infrastructure Controller (Cisco APIC) manages the model of the ACI fabric in a hierarchical (tree) structure. At the top of the tree structure is the root (*topRoot*) and the policy Universe (*polUni*) is contained by topRoot. 

The challenge in using a spreadsheet to represent the configuration of the ACI fabric focuses on optimizing and eliminating redundancy in the tabular format of the sheet to a hierarchal structure of the APIC Management Information Tree (MIT). 

### Elimination of Manual Operations

While the network administrator can manually issue a `File -> Save As` in Excel to create the CSV ("comma-separated values") files needed for the work-flow, this manual operation can be done programatically.

The benefits of developing a programmatic interface include the following:

* Sheet names are verified to be valid file names 
* Column headers verfied to be valid variable names 
* The playbook defines and extracts only the necessary sheet(s) from the spreadsheet file
* Eliminates human error in saving sheets

Note: the spreadsheet file can be stored in a SCM (Source Code Management System) with the Ansible playbooks, or downloaded by the playbook using the `uri` module.

#### Create CSV 

The module  `library/xls_to_csv.py`  reads an Excel .xlsx file and writes .csv files.

Given an input file *Excel_TEST_DATA.xlsx*  which contains three sheets, *"Tenant Policy"*, *"DHCP_Relay"*, and *"dhcp_servers"*, running the module as an ad-hoc command with an empty string for the sheets to select and the *warn* option will output the names of the sheets located in the source file. 

```bash
$ ansible localhost -m xls_to_csv -a "src='/it-automation-aci/TEST_DATA/Excel_TEST_DATA.xlsx' dest=/tmp sheets='' warn=true"
 [WARNING]: sheet "Tenant Policy" found in source file, skipping

 [WARNING]: sheet "DHCP_Relay" found in source file, skipping

 [WARNING]: sheet "dhcp_servers" found in source file, skipping

localhost | SUCCESS => {
    "ansible_facts": {
        "sheet_filenames": []
    },
    "changed": false
}
```
#### Naming Requirement
The program includes a function to convert the sheet names and column headers to valid file and variable names. Ansible variable names must be letters, numbers and underscores and must start with a letter. Special characters (other than an underscore) are removed and are spaces.

Running the module as an ad-hoc command and specifying the sheet "Tenant Policy", see that the module removed the embedded space in the sheet named "Tenant Policy" and exported the contents to */tmp/TenantPolicy*.

```bash
$ ansible localhost -m xls_to_csv -a "src='/it-automation-aci/TEST_DATA/Excel_TEST_DATA.xlsx' dest=/tmp sheets='Tenant Policy' warn=false"
localhost | CHANGED => {
    "ansible_facts": {
        "sheet_filenames": [
            "TenantPolicy"
        ]
    },
    "changed": true
}

```
#### Determine the column headers
The column headers of the CSV file can be identified by looking at the first record in the output file.
```bash
$ head -1 /tmp/TenantPolicy.csv
BD,Subnet,L2UnknownUnicast,AppProfile,Scope,Notes,VLAN,DC,DHCPRelayLabels,UnicastRouting,L3Out,Connectivity,VLANName,VRF,DHCP,ARPFlooding,EPG,GatewayAddress,Tenant

```
Knowing the column headers is important for converting the CSV file to Ansible facts in the `csv_to_facts` module described later.

#### TODO

Individual sheets in the spreadsheet file are extracted and written to a file. 

The playbook `test_xls.yml` includes an example of how to execute this module within a playbook. Review that file and focus on the following task:

```yaml

  tasks:
    - name: Extract the sheets from the Excel file, creating CSV files
      xls_to_csv:
        src: '{{ spreadsheet }}'
        dest: '{{ dest }}'
        sheets:
          - 'Tenant Policy'
          - 'DHCP_Relay'
          - 'dhcp_servers'
        warn: True
```
**Tip:** As a best practice, use '{{ playbook_dir }}/files' as the destination directory. To avoid any file permission errors when running your playbook from Ansible Tower.

From running the module as an Ansible ad-hoc command, we can identify the names of the sheets in the spreadsheet file. The *sheets* variable is a list of sheets we wish to extract from the spreadsheet file and write the result to individual CSV files. Execute the `test_xls.yml` playbook and specify the tag *xls_to_csv* which identifies the first play in the YAML file.

```bash
$ ./test_xls.yml --tags xls_to_csv

PLAY [localhost] **************************************************************************************************************

TASK [Extract the sheets from the Excel file, creating CSV files] *************************************************************
changed: [localhost]

TASK [debug] ******************************************************************************************************************
ok: [localhost] => (item=DHCP_Relay) => {}

MSG:
File /tmp/foo/DHCP_Relay has been created

ok: [localhost] => (item=TenantPolicy) => {}

MSG:
File /tmp/foo/TenantPolicy has been created

ok: [localhost] => (item=dhcp_servers) => {}

MSG:
File /tmp/foo/dhcp_servers has been created

PLAY [localhost] **************************************************************************************************************

PLAY RECAP ********************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0

```



### Data Types
