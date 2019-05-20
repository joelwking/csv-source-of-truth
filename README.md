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
The module has a function to convert the sheet names and column headers to valid file and variable names. Ansible variable names must be letters, numbers and underscores and must start with a letter. The function removes special characters (other than an underscore) and spaces. 

Run the module as an ad-hoc command and specifying the sheet "Tenant Policy", note the module removed the embedded space in the sheet named "Tenant Policy" and exported the contents to */tmp/TenantPolicy*.

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
Individual sheets in the spreadsheet file are extracted and written to files. The module returns a list variable *sheet_filenames* which specifies the filenames of the extracted sheets in the destination directory.

#### Playbook Example

This section illustrates running the `xls_to_csv` module from a playbook.

Review `test_xls.yml`. The `xls_to_csv` module is executed specifying the source spreadsheet file, a destination directory to write the selected sheets, and a list of sheets to extract from the spreadsheet file.

```yaml
- hosts: localhost
  gather_facts: no 
  connection: local
  tags: [play1, xls_to_csv]

  vars:
    spreadsheet: '/it-automation-aci/TEST_DATA/Excel_TEST_DATA.xlsx'  
    dest: '{{ playbook_dir }}/files/aci/'

  tasks:
    - name: Extract the sheets from the Excel file, creating CSV files 
      xls_to_csv:
        src: '{{ spreadsheet }}' 
        dest: '{{ dest }}' 
        sheets: 
          - 'Tenant Policy'
          - 'DHCP_Relay'
          - 'dhcp_servers'
```
**Tip:** As a best practice, use '{{ playbook_dir }}/files' as the destination directory. To avoid any file permission errors when running your playbook from Ansible Tower.

From running the module as an Ansible ad-hoc command, we can identify the names of the sheets in the spreadsheet file. The *sheets* variable is a list of sheets we wish to extract from the spreadsheet file and write the result to individual CSV files. Execute the `test_xls.yml` playbook and specify the tag *play1* which identifies the first play in the YAML file.

```bash
$ ./test_xls.yml --tags play1

PLAY [localhost] **********************************************************************************************

TASK [Extract the sheets from the Excel file, creating CSV files] *********************************************
changed: [localhost]

TASK [debug] **************************************************************************************************
ok: [localhost] => (item=DHCP_Relay) => {}

MSG:
File /home/administrator/ansible/playbooks/files/aci/DHCP_Relay has been created
ok: [localhost] => (item=TenantPolicy) => {}

MSG:
File /home/administrator/ansible/playbooks/files/aci/TenantPolicy has been created
ok: [localhost] => (item=dhcp_servers) => {}

MSG:
File /home/administrator/ansible/playbooks/files/aci/dhcp_servers has been created

PLAY [localhost] **********************************************************************************************

PLAY RECAP ****************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0
```

#### Determine the column header names
The column headers of the CSV file can be identified by looking at the first record in the output file.
```bash
$ head -1 ./files/aci/*.csv
==> ./files/aci/DHCP_Relay.csv <==
BD,AppProfile,Notes,DC,DHCPRelayLabels,DHCP,EPG,Tenant

==> ./files/aci/dhcp_servers.csv <==
hostname,addr,fqdn,label

==> ./files/aci/TenantPolicy.csv <==
BD,Subnet,L2UnknownUnicast,AppProfile,Scope,Notes,VLAN,DC,DHCPRelayLabels,UnicastRouting,L3Out,Connectivity,VLANName,VRF,DHCP,ARPFlooding,EPG,GatewayAddress,Tenant
```
Because the column headers are used as variable names referenced in playbooks, issue the `head -1` command for each file to identify the column headers.  

**Tip:** Knowing the column headers is important for converting the CSV file to Ansible facts in the `csv_to_facts` module described later.

#### Summary
This section illustrates programmatically extracting one or more sheets from a spreadsheet file. This enables the network engineer to use a spreadsheet program, like Microsoft Excel, to define the initial state of the network infrastructure. The `xls_to_csv` module is used to identify and extract the sheet names in the spreadsheet file, writing the contents of the sheet to a CSV formatted file.

By reviewing the column headers in the output files, the cell contents of each row can be used as configuration data for the network infrastructure.

#### Read CSV, expose as variables to a playbook

The module `csv_to_facts` reads a CSV file and returns as Ansible facts a list of dictionaries for each row. The column header is the key, the contents of the cell is the value.

For example, assume there are two data centers, (DC1 and DC2) each with an APIC Clusters managing the policy of their respective domain. Each data center will have one or more tenants, each tenant may have one or more VRFs, Bridge Domains, and so on. The tabular data, therefore, will have redundant information at the root of the tree.

Looking at the sample data (file TenantPolicy.csv), there are 15 rows of data, representing two data centers, with each data center having two tenants.

While there are a number of columns in each row that describe the configuration of the ACI fabric(s), for this explanation we will focus on the column *DC* (data center), and *Tenant*.

```bash
$ cat files/aci/TenantPolicy.csv | cut -d ',' -f 8,20
DC,Tenant
DC1,XXV-INT
DC1,XXV-DMZ
DC2,XXV-DMZ
DC1,XXV-INT
DC1,XXV-INT
DC1,XXV-INT
DC1,XXV-DMZ
DC1,XXV-DMZ
DC1,XXV-INT
DC1,XXV-DMZ
DC1,XXV-DMZ
DC2,XXV-INT
DC2,XXV-INT
DC2,XXV-INT
DC2,XXV-INT
```

#### Execute csv_to_facts
The module `csv_to_facts` reads a CSV file and returns as Ansible facts a list of dictionaries for each row. The column header is the key, the contents of the cell is the value.

The default behavior of `csv_to_facts` is to return as facts the content of the source (*src*) file in a list variable named *spreadsheet*. Examine this playbook sample.

```yaml
- hosts: localhost
  gather_facts: no
  tags: [play2, csv_to_facts]

  tasks:
    - name: Default behavior of csv_to_facts
      csv_to_facts:
        src: '{{ playbook_dir }}/files/aci/TenantPolicy.csv'

    - debug:
        msg: '{{ item.DC }} {{ item.Tenant }}'
      loop: '{{ spreadsheet }}'

```

By executing the playbook, we iterate over the list variable *spreadsheet* and reference the *DC* and *Tenant* columns. The list spreadsheet has a length of 15, each list item corresponds to a row in the CSV file.

**Tip:** The argument *table* can be specified to provide a value other than the default value of *spreadsheet*. Use `ansible-doc csv_to_facts` for more details.

### Optimizing Tabular Data
Because a spreadsheet represents data in a tabular format, and the ACI fabric configuration is stored in a Management Information Tree (a hierarchical) structure, there will be repetitive data defined in the sheet.

In the use case of configuring the ACI fabric from this data, the APIC REST API itself is idempotent, issuing a request to create (or delete) a tenant with the same name does not add a duplicate tenant, it simply validates the tenant name exists (or in the case of a delete, it doesn't exist), and returns a successful status (200 OK) to the caller.

However, this is inefficient, causing unnecessary API calls and increasing the run time and memory usage of the playbook.

#### Create virtual spreadsheets
The `csv_to_facts` module can optimize the input file by creating a fact variable which eliminates redundancy by returning unique rows for the columns specified. 

This optimization of the input CSV file is a accomplished by creating multiple views of the input data with the specified columns and returning a list of unique values for the column specified. 

This is accomplished by manipulating the input spreadsheet and using the Python *set* data type to create unordered collections of unique elements. 

These virtual spreadsheets can be used to loop (iterate) over a task. In Ansible, loops are used to repeat a task multiple times.

To illustrate, given the input *files/aci/TenantPolicy.csv* and a role / task file which will create an ACI tenant, the goal is to iterate over this task, selecting data center *DC1* and creating (or deleting) the Tenants specified in the CSV file.

```yaml
  vars:
    data_center: 'DC1'
    change_request: 'CHG00012345'

  tasks:
    - name: Manage Tenants
      include_role:
        name: ansible-aci-tenant
        tasks_from: tenant
      vars:
        fvTenant:
          name: '{{ item.Tenant }}'
          descr: '{{ change_request }}'
      loop: '{{ TENANTs }}'
      when:
        - item.DC == data_center
```

To accomplish this task, our list variable *TENANTs* should look like the following data structure:

```json
{
    "ansible_facts": {
        "TENANTs": [
            {
                "DC": "DC2",
                "Tenant": "XXV-INT"
            },
            {
                "DC": "DC1",
                "Tenant": "XXV-DMZ"
            },
            {
                "DC": "DC2",
                "Tenant": "XXV-DMZ"
            },
            {
                "DC": "DC1",
                "Tenant": "XXV-INT"
            }
        ]
}
```
