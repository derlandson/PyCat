# PyCat
Code for poster presentation

Code requires the following libraries: io, json, os, pandas, bookops_worldcat, and pymarc

Code utilizes the OCLC Worldcat Metadata API, individuals will need to be able to gather the appropriate credentials

Developed in a Mac environment, may have to adjust some code for a windows environment when locating json creds file

Utilizes a read from google sheet feature, users will need to supply their own gsheet id


PyCat will gather identified records from a sheet of OCLC/MMS ID pairs

Adds a 590 note

Changes the 001 (mentioned above) from OCLC ID to MMS ID to allow an accurate overlay via Alma Import Profile feature

Removes a list of fields, configurable. Currently: 015, 016, 017, 019, 029, 055, 060, 070, 072, 082, 084, 263, 856, 938

Tests subjects for ind2 == 7, removes if so. Configurable. Applies to: 600, 610, 611, 630, 647, 648, 650, 651, 653, 654, 655, 656, 657, 658, 662

Writes clean records to a "retrieved_bibs.mrc" file ready to import to Alma
