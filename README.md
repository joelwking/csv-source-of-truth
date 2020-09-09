# csv-source-of-truth
Collection of modules and documentation to enable using Microsoft Excel (and CSV files) as a Source of Truth for configuration data.

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/joelwking/csv-source-of-truth)

## Overview
The goal of this effort is to enable using a on-line or local spreadsheet program (Microsoft Excel) to define the configuration of a network fabric. The use case which prompted this development is automating the configuration of Cisco Application Centric Infrastructure (ACI) using Ansible. However, these modules have value to other devices in the network infrastructure.

## Why use a Spreadsheet?
Microsoft Excel is readily available, provides a high degree of functionality for data visualization and analysis, and is commonly used by network engineers for the definition of data center fabrics.

While YAML is a human-readable data serialization language and perhaps more suitable, especially given using Ansible as a configuration management tool, the whitespace indentation to provide structure can be confusing initially to the non-programmer.

### Data Structure
Spreadsheets represent data in a tabular data format similar to a relational database. The database stores data in objects called tables, which consist of columns and rows. The columns include a column name and other attributes.

The spreadsheet file (.xlsx) is analogous to a database, while one or more *sheets* in the file are analogous to tables in the database. 

In our use case, configuring a Cisco ACI fabric, the Cisco Application Policy Infrastructure Controller (Cisco APIC) manages the model of the ACI fabric in a hierarchical (tree) structure. At the top of the tree structure is the root (*topRoot*) and the policy Universe (*polUni*) is contained by topRoot. 

The challenge in using a spreadsheet to represent the configuration of the ACI fabric focuses on optimizing and eliminating redundancy in the tabular format of the sheet to a hierarchal structure of the APIC Management Information Tree (MIT).

### Elimination of Manual Operations
While the network administrator can manually issue a `File -> Save As` in Excel to create the CSV ("comma-separated values") files needed for the work-flow, this manual operation can be done programmatically.

The benefits of developing a programmatic interface include the following:

* Sheet names are verified to be valid file names 
* Column headers verified to be valid variable names 
* The playbook specifies and extracts only the necessary sheet(s) from the spreadsheet file
* Eliminates human error in saving sheets

The spreadsheet file can be stored in a SCM (Source Code Management System) with the Ansible playbooks, or downloaded by the playbook using the `uri` module.

## What is Included?

This repository contains the following modules in the `/library/` directory:

- `xls_to_csv.py`    Reads an Excel .xlsx file and output .csv files for each sheet specified
- `csv_to_facts.py`  Reads a CSV file and returns as ansible facts a list of dictionaries for each row

The two modules can be executed in sequence. For example, `xls_to_csv.py` can be used to extract sheets from a spreadsheet into individual CSV files, and in a subsequent task or play, `csv_to_facts.py` can be used to expose the data from a CSV file as variables to a playbook. Either module can be used independently of the other. 

The module `csv_to_facts.py` was originally developed in 2015. It remains at the [original](https://github.com/joelwking/ansible-nxapi) (now deprecated) location. The design goal of these modules subscribes to the UNIX philosophy of 

> *Make each program do one thing well. To do a new job, build afresh rather than complicate old programs by adding new "features".* 

which is why `xls_to_csv.py` was developed as a separate module.

## Installation

If your intent is to use these modules with Ansible Tower or with a multi-user system, you may which to install them in a common location on an existing system. You can also use an ephemeral environment using Vagrant.

### Requirements
Python packages **pandas** and **xlrd** are required if using `library/xls_to_csv.py`. They can be installed using Pip.
```
$ sudo pip install xlrd pandas
```
or if using Python3
```
$  sudo pip3 install xlrd pandas
```

### How to Test the Software
If you have Ansible Tower installed on an existing system you can download the modules to a shared directory and modify the Ansible configuration file to identify the location.

Alternately, you can create an ephemeral test environment using Vagrant.

#### Install to an Existing System
Refer to the instructions for [Adding modules and plugins locally.](https://docs.ansible.com/ansible/latest/dev_guide/developing_locally.html)

The modules `library/xls_to_csv.py` and `library/csv_to_facts.py` can be written to the Ansible 'magic' directories.  Modify the `/etc/ansible/ansible.cfg` file to include:

```
library        = /usr/share/ansible/
```
Then use *wget* to download these modules to that directory:
```
$ cd /usr/share/ansible
$ sudo wget https://raw.githubusercontent.com/joelwking/csv-source-of-truth/master/library/csv_to_facts.py
$ sudo wget https://raw.githubusercontent.com/joelwking/csv-source-of-truth/master/library/xls_to_csv.py
$ chmod 755 *.py
```
To verify installation, issue `ansible-doc csv_to_facts`.

#### Install using Vagrant
Alternately, if you only wish to create a test environment using [Vagrant](https://www.vagrantup.com/), there is a sample configuration file in `files/vagrant/`.  After issuing the `vagrant up` command using the Vagrantfile in this repository, `vagrant ssh` and complete the configuration with the following commands:

```bash
$ git clone https://github.com/joelwking/csv-source-of-truth.git
$ export ANSIBLE_LIBRARY=$HOME/csv-source-of-truth/library
$ export ANSIBLE_DEPRECATION_WARNINGS=False
$ sudo pip install xlrd pandas
$ sudo pip3 install xlrd pandas
$ cd csv-source-of-truth
```
---
**Note:** This README file was tested using the Ansible 2.9.13 release.

## Usage
This section illustrates using the modules to extract and manipulate data used for configuring a Cisco ACI fabric. A sample spreadsheet is available in `files/aci/`. You may wish familiarize yourself with the contents of that spreadsheet prior to completing the following examples.

> **Note**: The inventory file `./files/inventory/yml` defines a group name of *python*, which has two localhosts, one for Python 2.7.17 and Python 3.6.9. You do not need to run the sample playbooks using both versions, it is to verify the code functions using either version.

### Create CSV 
The module  `library/xls_to_csv.py`  reads an Excel .xlsx file and writes .csv file(s).

The sample  input file `files/aci/ACI_DHCP_configuration.xlsx`  contains two sheets, *"DHCP Relay"*, and *"data_centers"*. 

The module is executed as an Ansible *ad-hoc* command to verify the sheet names. Run the module with an empty string for the *sheets* argument and the *warn* option to verify the sheet names. The module reports the names of the sheets located in the source file.  By using the host name of `python` and the `inventory.yml` file, both Python 2 and Python 3 are verified.

```bash
vagrant@ubuntu-bionic:~/csv-source-of-truth$ ansible python -m xls_to_csv -a "src='$HOME/csv-source-of-truth/files/aci/ACI_DHCP_configuration.xlsx' dest=/tmp sheets='' warn=true" -i ./files/inventory.yml
/usr/lib/python2.7/dist-packages/ansible/parsing/vault/__init__.py:44: CryptographyDeprecationWarning: Python 2 is no longer supported by the Python core team. Support for it is now deprecated in cryptography, and will be removed in a future release.
  from cryptography.exceptions import InvalidSignature
[WARNING]: sheet "DHCP Relay" found in source file, skipping
[WARNING]: sheet "data_centers" found in source file, skipping
python2 | SUCCESS => {
    "ansible_facts": {
        "sheet_filenames": []
    },
    "changed": false
}
python3 | SUCCESS => {
    "ansible_facts": {
        "sheet_filenames": []
    },
    "changed": false
}
```
Because no sheets were written, the changed flag is set to 'false'.

#### Naming Requirement
The module converts the sheet names and column headers to valid file and variable names. Ansible variable names must be letters, numbers and underscores and must start with a letter. The module removes special characters (other than an underscore) and spaces. 

Run the module as an ad-hoc command and specifying the sheet "DHCP Relay". Note the module removed the embedded space in the sheet named "DHCP Relay" and exported the contents to */tmp/DHCPRelay*.

```bash
vagrant@ubuntu-bionic:~/csv-source-of-truth$ ansible python -m xls_to_csv -a "src='$HOME/csv-source-of-truth/files/aci/ACI_DHCP_configuration.xlsx' dest=/tmp sheets='DHCP Relay'" -i ./files/inventory.yml
/usr/lib/python2.7/dist-packages/ansible/parsing/vault/__init__.py:44: CryptographyDeprecationWarning: Python 2 is no longer supported by the Python core team. Support for it is now deprecated in cryptography, and will be removed in a future release.
  from cryptography.exceptions import InvalidSignature
python2 | CHANGED => {
    "ansible_facts": {
        "sheet_filenames": [
            "DHCPRelay"
        ]
    },
    "changed": true
}
python3 | CHANGED => {
    "ansible_facts": {
        "sheet_filenames": [
            "DHCPRelay"
        ]
    },
    "changed": true
}

```
Individual sheets in the spreadsheet file are extracted and written to file(s). The module returns a variable *sheet_filenames* which is a list filenames of the extracted sheets saved in the destination directory.

#### Executing from a Playbook
This section illustrates running the `xls_to_csv` module from a playbook.

Review `test_xls.yml`. The `xls_to_csv` module is executed specifying the source spreadsheet file, a destination directory to write the selected sheets, and a list of sheets to extract from the spreadsheet file.

```yaml
- hosts: python
  gather_facts: no 
  connection: local
  tags: [play1, xls_to_csv]

  vars:
    spreadsheet: '{{ playbook_dir }}/files/aci/ACI_DHCP_configuration.xlsx'  
    dest: '{{ playbook_dir }}/files/aci/'

  tasks:
    - name: Extract the sheets from the Excel file, creating CSV files 
      xls_to_csv:
        src: '{{ spreadsheet }}' 
        dest: '{{ dest }}' 
        sheets: 
          - 'DHCP Relay'
          - 'data_centers'
        warn: True

    - debug:
        msg: 'File {{ dest }}{{ item }}.csv has been created'
      loop: '{{ sheet_filenames }}'
      tags: [debug]

```
---
**Tip:** As a best practice, specify your source and target directories relative to the playbook directory, for example: '{{ playbook_dir }}/files' as the destination directory. 

Running the module as an Ansible ad-hoc command, we can identify the names of the sheets in the spreadsheet file. The *sheets* variable is a list of sheets we wish to extract from the spreadsheet file and write the result to individual CSV files. Execute the `test_xls.yml` playbook and specify the tag *play1* which identifies the first play in the YAML file.

This step extracts the selected sheets and writes them to the destination directory.

```bash
vagrant@ubuntu-bionic:~/csv-source-of-truth$ ansible-playbook ./test_xls.yml --tags play1 -i ./files/inventory.yml
/usr/lib/python2.7/dist-packages/ansible/parsing/vault/__init__.py:44: CryptographyDeprecationWarning: Python 2 is no longer supported by the Python core team. Support for it is now deprecated in cryptography, and will be removed in a future release.
  from cryptography.exceptions import InvalidSignature

PLAY [python] *****************************************************************************************************************

TASK [Extract the sheets from the Excel file, creating CSV files] **************************************************************
changed: [python2]
changed: [python3]

TASK [debug] *******************************************************************************************************************
ok: [python3] => (item=DHCPRelay) => {
    "msg": "File /home/vagrant/csv-source-of-truth/files/aci/DHCPRelay.csv has been created"
}
ok: [python3] => (item=data_centers) => {
    "msg": "File /home/vagrant/csv-source-of-truth/files/aci/data_centers.csv has been created"
}
ok: [python2] => (item=data_centers) => {
    "msg": "File /home/vagrant/csv-source-of-truth/files/aci/data_centers.csv has been created"
}
ok: [python2] => (item=DHCPRelay) => {
    "msg": "File /home/vagrant/csv-source-of-truth/files/aci/DHCPRelay.csv has been created"
}

...

PLAY RECAP *************************************************************************************************************************
python2                    : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
python3                    : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

Next review the contents of the output file(s).

#### Determine the Column Header Names
The column headers of the CSV file(s) can be identified by looking at the first record in each output file.

```bash
vagrant@ubuntu-bionic:~/csv-source-of-truth$ head -1 ./files/aci/*.csv
==> ./files/aci/DHCPRelay.csv <==
DC,Tenant,VRF,BD,AppProfile,EPG,VLAN,DHCP,L3Out

==> ./files/aci/data_centers.csv <==
DC,Tenant,fullname,address1,city,state,postalcode
vagrant@ubuntu-bionic:~/csv-source-of-truth$
```

Because the column headers are used as variable names by playbooks, issue the `head -1` command for each file to identify the column headers.  

---
**Tip:** Knowing the column headers is important for converting the CSV file to Ansible facts in the `csv_to_facts` module described later.

#### Summary
This section illustrates programmatically extracting one or more sheets from a spreadsheet file. This enables the network engineer to use a spreadsheet program, like Microsoft Excel, to define the initial state of the network infrastructure. The `xls_to_csv` module is used to identify and extract the sheet names in the spreadsheet file, writing the contents of the sheet to a CSV formatted file.

By reviewing the column headers in the output files, the cell contents of each row can be used as configuration data for the network infrastructure.

### Read CSV
The module `library/csv_to_facts.py` reads a CSV file and returns as Ansible facts a list of dictionaries for each row. The column header is the key, the contents of the cell is the value.

For example, assume there are two data centers, (DC1 and DC2) each with an APIC Clusters managing the policy of their respective domain. Each data center will have one or more tenants, each tenant may have one or more VRFs, Bridge Domains, and so on. The tabular data, therefore, will have redundant information at the root of the tree.

Looking at the sample data (file DHCPRelay.csv), there are 15 rows of data, representing two data centers, with each data center having two tenants.

While there are a number of columns in each row that describe the configuration of the ACI fabric(s), for this explanation we will focus on the column *DC* (data center), and *Tenant*.

```bash
vagrant@ubuntu-bionic:~/csv-source-of-truth$ cat ./files/aci/DHCPRelay.csv | cut -d ',' -f 1,2
DC,Tenant
DC1,XXV-INT
DC1,XXV-DMZ
DC2,XXV-DMZ
DC1,XXV-INT
DC1,XXV-INT
DC1,XXV-INT
DC1,XXV-INT
DC1,XXV-INT
DC1,XXV-INT
DC1,XXV-INT
DC1,XXV-INT
DC2,XXV-INT
DC2,XXV-INT
DC2,XXV-INT
DC2,XXV-INT
```

#### Execute csv_to_facts
The module `csv_to_facts` reads a CSV file and returns as Ansible facts a list of dictionaries for each row. The column header is the key, the contents of the cell is the value.

The default behavior of `csv_to_facts` is to return  the content of the source (*src*) file in a list variable named *spreadsheet*. Examine this playbook sample.

```yaml
- hosts: python
  gather_facts: no
  tags: [play2, csv_to_facts]

  tasks:
    - name: Default behavior of csv_to_facts
      csv_to_facts:
        src: '{{ playbook_dir }}/files/aci/DHCPRelay.csv'
    - debug:
        msg: '{{ item.DC }} {{ item.Tenant }}'
      loop: '{{ spreadsheet }}'

```

By executing the playbook, we iterate over the list variable *spreadsheet* and reference the *DC* and *Tenant* columns. The list variable *spreadsheet* has a length of 15, each item corresponds to a row in the CSV file.

Execute play2 to verify the debug module can reference the variables specified in the CSV file.

```bash
vagrant@ubuntu-bionic:~/csv-source-of-truth$ ansible-playbook ./test_xls.yml --tags play2 -i ./files/inventory.yml
/usr/lib/python2.7/dist-packages/ansible/parsing/vault/__init__.py:44: CryptographyDeprecationWarning: Python 2 is no longer supported by the Python core team. Support for it is now deprecated in cryptography, and will be removed in a future release.
  from cryptography.exceptions import InvalidSignature

PLAY [python] ******************************************************************************************************************

PLAY [python] ******************************************************************************************************************

TASK [Default behavior of csv_to_facts] ****************************************************************************************
ok: [python2]
ok: [python3]

TASK [debug] ***********************************************************************************************************************
ok: [python3] => (item={u'BD': u'BD-BOX-RAZOR', u'AppProfile': u'AP-PRD', u'VLAN': u'39', u'DC': u'DC1', u'L3Out': u'ERN-N7KCORESW-L3OUT', u'VRF': u'VRF-XXV-INT', u'DHCP': u'Yes', u'EPG': u'EPG-BOX-RAZOR', u'Tenant': u'XXV-INT'}) => {
    "msg": "DC1 XXV-INT"
}
```
---
**Note:** The output of the above execution was truncated for brevity, only the first row was shown. 

**Tip:** The argument *table* can be specified to provide a value other than the default value of *spreadsheet*. Use `ansible-doc csv_to_facts` for more details.

#### Optimizing Tabular Data
Because a spreadsheet represents data in a tabular format, and the ACI fabric configuration is stored in a Management Information Tree (a hierarchical) structure, there will be repetitive data defined in the sheet.

The APIC REST API itself is idempotent, issuing a request to create (or delete) a tenant with the same name does not add a duplicate tenant, it simply validates the tenant name exists (or in the case of a delete, it doesn't exist), and returns a successful status (200 OK) to the caller.

However, this is inefficient, causing unnecessary API calls and increasing the run time and memory usage of the playbook. 

If the data were loaded into a relational database, SQL provides a **SELECT DISTINCT** statement to return only distinct (different) values. Relational database tables often contain duplicate values. In this example the goal is to return only the unique (distinct) values.

In SQL, the statement might look like the following:
```sql
SELECT DISTINCT DC, Tenant FROM DHCPRelay;
```
In the next section, `csv_to_facts` can be configured to return distinct values for the columns specified.

#### Create virtual spreadsheets
The `csv_to_facts` module can optimize the input file by creating a variable which eliminates redundancy by returning unique (distinct) values for the columns specified. 

This optimization of the input CSV file is a accomplished by creating multiple views of the input data with the specified columns and returning a list of unique values for the column specified. 

This is accomplished by manipulating the input spreadsheet and using the Python *set* data type to create unordered collections of unique elements. 

These virtual spreadsheets can be used to loop (iterate) over a task. Ansible uses loops (or *with_items*) to repeat a task multiple times.

As an example, assume there is a task file (*tenant* in role *ansible-aci-tenant*) which creates an ACI tenant, the goal is to iterate over this task, creating (or deleting) the Tenants for data center *DC1* specified in the CSV file.

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

To accomplish this task efficiently, our list variable *TENANTs* should be made up of the unique tenants in each data center. Each data center has the same two tenants, *XXV-INT* and *XXV-DMZ*. 

The goal is to create a list variable TENANTs with only four entries from the 15 rows in the original spreadsheet.

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
By using the *vsheets* argument, specify a list of virtual spreadsheets you wish to create, and for each virtual spreadsheet, specify a list of columns.  The aforementioned list of *TENANTs* can be created using the following example:

```yaml
- hosts: localhost
  gather_facts: no
  tags: [play3, csv_to_facts]

  tasks:
    - name: Create virtual spreadsheet of data centers (DC) and tenants
      csv_to_facts:
        src: '{{ playbook_dir }}/files/aci/DHCPRelay.csv'
        vsheets: 
          - TENANTs:
             - DC
             - Tenant
```

Executing the play with verbose mode (*-v*) illustrates the variable TENANTs is a list of unique values of columns DC and Tenant.

```bash
vagrant@ubuntu-bionic:~/csv-source-of-truth$ ansible-playbook ./test_xls.yml --tags play3 -i ./files/inventory.yml -v
/usr/lib/python2.7/dist-packages/ansible/parsing/vault/__init__.py:44: CryptographyDeprecationWarning: Python 2 is no longer supported by the Python core team. Support for it is now deprecated in cryptography, and will be removed in a future release.
  from cryptography.exceptions import InvalidSignature
Using /etc/ansible/ansible.cfg as config file

PLAY [python] *****************************************************************************************************************

PLAY [python] *****************************************************************************************************************

PLAY [python] *****************************************************************************************************************

TASK [Create virtual spreadsheet of data centers (DC) and tenants] *************************************************************
ok: [python2] => {"ansible_facts": {"TENANTs": [{"DC": "DC2", "Tenant": "XXV-INT"}, {"DC": "DC1", "Tenant": "XXV-DMZ"}, {"DC": "DC2", "Tenant": "XXV-DMZ"}, {"DC": "DC1", "Tenant": "XXV-INT"}], "spreadsheet": [{"AppProfile": "AP-PRD", "BD": "BD-BOX-RAZOR", "DC": "DC1", "DHCP": "Yes", "EPG": "EPG-BOX-RAZOR", "L3Out": "ERN-N7KCORESW-L3OUT", "Tenant": "XXV-INT", "VLAN": "39", "VRF": "VRF-XXV-INT"}
```
---
**Note:** The output of the above execution was truncated for brevity.

#### Sheet Filenames
The module `xls_to_csv` returns the variable `sheet_filenames`.  This variable can be referenced in subsequent tasks or plays to identify the names of the files created.

By executing plays 1 and 4, the variable `sheet_filenames` can be referenced in subsequent play(s). Execute these plays by specifying their tags. 

```bash
vagrant@ubuntu-bionic:~/csv-source-of-truth$  ansible-playbook ./test_xls.yml --tags 'play1, play4' -i ./files/inventory.yml
/usr/lib/python2.7/dist-packages/ansible/parsing/vault/__init__.py:44: CryptographyDeprecationWarning: Python 2 is no longer supported by the Python core team. Support for it is now deprecated in cryptography, and will be removed in a future release.
  from cryptography.exceptions import InvalidSignature

PLAY [python] ******************************************************************************************************************

TASK [Extract the sheets from the Excel file, creating CSV files] **************************************************************
changed: [python2]
changed: [python3]

TASK [debug] *******************************************************************************************************************
ok: [python3] => (item=DHCPRelay) => {
    "msg": "File /home/vagrant/csv-source-of-truth/files/aci/DHCPRelay.csv has been created"
}
ok: [python3] => (item=data_centers) => {
    "msg": "File /home/vagrant/csv-source-of-truth/files/aci/data_centers.csv has been created"
}
ok: [python2] => (item=data_centers) => {
    "msg": "File /home/vagrant/csv-source-of-truth/files/aci/data_centers.csv has been created"
}
ok: [python2] => (item=DHCPRelay) => {
    "msg": "File /home/vagrant/csv-source-of-truth/files/aci/DHCPRelay.csv has been created"
}

PLAY [python] ******************************************************************************************************************

PLAY [python] ******************************************************************************************************************

PLAY [python] ******************************************************************************************************************

TASK [Create summarized virtual sheets, loading the variables in a namespace using the filename] *******************************
ok: [python2] => (item=data_centers)
ok: [python3] => (item=DHCPRelay)
ok: [python2] => (item=DHCPRelay)
ok: [python3] => (item=data_centers)

TASK [debug] *******************************************************************************************************************
ok: [python3] => (item={u'address1': u'6007 Applegate Lane', u'DC': u'DC2', u'Tenant': u'XXV-DMZ'}) => {
    "msg": {
        "DC": "DC2",
        "Tenant": "XXV-DMZ",
        "address1": "6007 Applegate Lane"
    }
}

```
---
**Note:** The output of the above execution was truncated for brevity.

### Sample Use Case

To illustrate the use of both the `xls_to_csv` and the `csv_to_facts` modules, 

Review the playbook *manage_aci_dhcp.yml*.  This playbook contains two plays. 

The first play uses `xls_to_csv` reading the input file located in *files/aci/ACI_DHCP_configuration.xlsx*, selects sheet 'DHCP Relay' and writes it to a CSV file in the same directory with a file name of 'DHCPRelay.csv'

The second play uses `csv_to_facts`. This module creates a list variable named *DHCPentries* which includes these columns from the sheet 'DHCP Relay'. 

```yaml
    - DC
    - Tenant
    - BD
    - AppProfile
    - DHCP
    - EPG
```

The second task (Associate multiple DHCP servers with a Tenant, Bridge Domain) in the play iterates over the list variable *DHCPentries* and all elements of *dhcp.server*, which is defined in `files/aci_dhcp.yml`.

Extra vars are passed from the command line to select the appropriate data center and test if the variable *DHCP* is True (specified as 'Yes' in the sheet).

In this example, the *debug* module is used as a placeholder for the appropriate Ansible ACI module(s). For more information on using Ansible to configure an ACI fabric, please refer to the [Cisco ACI Guide](https://docs.ansible.com/ansible/latest/scenario_guides/guide_aci.html).

```bash
vagrant@ubuntu-bionic:~/csv-source-of-truth$ ansible-playbook -i ./files/inventory.yml ./manage_aci_dhcp.yml -e "data_ce
> nter=DC1 ticket=CHG58234"
/usr/lib/python2.7/dist-packages/ansible/parsing/vault/__init__.py:44: CryptographyDeprecationWarning: Python 2 is no longer supported by the Python core team. Support for it is now deprecated in cryptography, and will be removed in a future release.
  from cryptography.exceptions import InvalidSignature

PLAY [localhost] ***************************************************************************************************************

TASK [Extract the sheets from the Excel file, creating CSV file(s)] ************************************************************
[WARNING]: sheet "data_centers" found in source file, skipping
changed: [localhost]

PLAY [APIC] ********************************************************************************************************************

TASK [Summarize the sheet and include as facts] ********************************************************************************
ok: [aci-demo.sandbox.wwtatc.local]

TASK [Associate multiple DHCP servers with a Tenant, Bridge Domain] ************************************************************
ok: [aci-demo.sandbox.wwtatc.local] => (item=[{u'BD': u'BD-BOX-PRVLIN1', u'AppProfile': u'AP-BOX', u'DHCP': u'Yes', u'EPG': u'EPG-BOX-PRVLIN1', u'DC': u'DC1', u'Tenant': u'XXV-INT'}, {u'value': {u'dn': u'uni/tn-WWT_NULL/ap-MANAGEMENT/epg-DHCP', u'addr': u'198.51.100.17'}, u'key': u'DHCP-DC2-PRD'}]) => {
    "msg": "Apply to tenant=XXV-INT BD=BD-BOX-PRVLIN1 DHCP Label=DHCP-DC2-PRD server=198.51.100.17 dn=uni/tn-WWT_NULL/ap-MANAGEMENT/epg-DHCP"
}
ok: [aci-demo.sandbox.wwtatc.local] => (item=[{u'BD': u'BD-BOX-PRVLIN1', u'AppProfile': u'AP-BOX', u'DHCP': u'Yes', u'EPG': u'EPG-BOX-PRVLIN1', u'DC': u'DC1', u'Tenant': u'XXV-INT'}, {u'value': {u'dn': u'uni/tn-common/out-L3-ATC/instP-L3-ATC', u'addr': u'203.0.113.17'}, u'key': u'DHCP-DC1-PRD'}]) => {
    "msg": "Apply to tenant=XXV-INT BD=BD-BOX-PRVLIN1 DHCP Label=DHCP-DC1-PRD server=203.0.113.17 dn=uni/tn-common/out-L3-ATC/instP-L3-ATC"
}
skipping: [aci-demo.sandbox.wwtatc.local] => (item=[{u'BD': u'BD-BOX-VMNFS2', u'AppProfile': u'AP-BOX', u'DHCP': u'Yes', u'EPG': u'EPG-BOX-VMNFS2', u'DC': u'DC2', u'Tenant': u'XXV-INT'}, {u'value': {u'dn': u'uni/tn-WWT_NULL/ap-MANAGEMENT/epg-DHCP', u'addr': u'198.51.100.17'}, u'key': u'DHCP-DC2-PRD'}])

```
---
**Note:** The output of the above execution was truncated for brevity.

**Tip:** Between play 1 and play 2, the variable *sheet* is a different format, the embedded space has been eliminated by module `xls_to_csv`.  This illustrates the importance of creating spreadsheet and column names that do not contain spaces or special characters.


For example, because "extra vars" take precedence, specifying *sheet* on the command line will cause the playbook to fail. To illustrate execute the following command:

```bash
vagrant@ubuntu-xenial:~/csv-source-of-truth$ ansible-playbook -i ./files/inventory.yml ./manage_aci_dhcp.yml -e "data_center=DC1 sheet='DHCP Relay' ticket=CHG58234"
```
#### Summary
This section illustrates reading one or more CSV files into variables. Additionally, module `csv_to_facts` can be configured to return virtual sheets which return only distinct (different) values. This feature implements the behavior of the SQL command *DISTINCT*, eliminating redundant rows and optimizing playbook execution.

## Synopsis
Organizing and managing the Source of Truth for configuring infrastructure is equally important to developing the process (workflow) to effect the configuration. Network engineers commonly use spreadsheets to represent network infrastructure which organize data in a tabular data format similar to a relational database. 

The modules and playbooks shown in this repository can be used to manipulate and import tabular data for managing infrastructure devices. 

## Known Issues
None.

## Getting Help
If you have questions or comments on network and infrastructure automation in general or these modules, please contact the author or AutomationTeam@wwt.com.

## Credits and References

* [Enabling policy migration in the Data Center with Ansible ](https://www.slideshare.net/joelwking/enabling-policy-migration-in-the-data-center-with-ansible) presented at the Ansible Durham Meetup 17April 2019
* [Super-NetOps Source of Truth ](https://www.slideshare.net/joelwking/supernetops-source-of-truth-110053045) presented at F5 Agility conference August 2018

## Author
Joel W. King (@joelwking) joel.king@wwt.com - Engineering and Innovations, Network Solutions, World Wide Technology