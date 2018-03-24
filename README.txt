halccli.py: a program to modify HAL entries (eg archives-ouvertes.fr) with command line or Python API using the REST Sword API.

Examples:
    halccli.py --id hal-01037383 --get_title
    ./halccli.py --id hal-01309004 --get_title --prod --user toto

To support ne1w fields, pull request on Github welcome.

Reference documents:
* Ref Hal doc: https://api.archives-ouvertes.fr/docs/sword
* Schema SWORD used in HAL: https://api.archives-ouvertes.fr/documents/aofr-sword.xsd
• Spec SWORD: http://swordapp.github.io/SWORDv2-Profile/SWORDProfile.html

Author: Martin Monperrus (August 2016)
License: Public Domain
URL: http://www.monperrus.net/martin/halccli

Usage:
  halccli.py --id <id> [--user <user>] [--pass <pass>] [--prod] [--set_title <title>] [--set_pages <pages>] [--set_doi <doi>] [--set_volume <volume>] [--set_institution <institution>] [--set_number <number>] [--set_comment <comment>] 
  halccli.py --id <id> [--user <user>] [--pass <pass>] [--prod] [--get_title] [--get_pages] [--get_doi] [--get_volume]  [--get_institution] [--get_number] [--get_comment]
  halccli.py --id <id> --tei [--prod]
 
Options:
  -h --help            Show this screen.
  --id <id>            Hal identifier.
  --prod               Use the production server(https://hal.archives-ouvertes.fr/) instead of the test one (https://hal-preprod.archives-ouvertes.fr/) [default: False].
  --user <user>        the user [default: test_ws]
  --pass <pass>        the password [default: test]
  --get_title          Gets the paper title
  --set_title <title>  Sets the paper title
  --get_pages          Gets the pages
  --set_pages <title>  Sets the pages
  --get_doi            Gets the DOI
  --set_doi <doi>      Sets the DOI
  --get_volume            Gets the volume
  --set_volume <volume>      Sets the volume
  --get_institution            Gets the institution
  --set_institution <institution>      Sets the institution
  --get_number            Gets the technical report number
  --set_number <number>      Sets the technical report number
  --get_comment            Gets the comment field
  --set_comment <comment>      Sets the comment field


