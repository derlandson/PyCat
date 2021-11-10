from io import BytesIO
import json
import os
import pandas as pd
from bookops_worldcat import WorldcatAccessToken, MetadataSession
from pymarc import XmlHandler, parse_xml, Field


# Sets up the XML handler to convert MarcXML to something less annoying
def parse_xml_record(data):
    handler = XmlHandler()
    parse_xml(data, handler)
    return handler.records[0]


# Defines a method of getting tokens with BookOps
# Separate file for security
# !!ADD YOUR OWN CREDS FILE TO THE SAME PYCAT LOCATION!!
def get_token():
    creds_fh = os.path.join(os.getenv("HOME"), "PycharmProjects/OCLCTools/my_wskey.json")
    with open(creds_fh, "r") as file:
        creds = json.load(file)
        token = WorldcatAccessToken(
            key=creds["key"],
            secret=creds["secret"],
            scopes=creds["scopes"],
            principal_id=creds["principal_id"],
            principal_idns=creds["principal_idns"],
            agent="de12@rice.edu"
        )
        return token


# Defines a new 590 to help track records in ILS
my_590 = Field(
    tag="590",
    indicators=["0", " "],
    subfields=["a", "Imported with PyCat."]
)

# Defines the list of OCLC numbers
# !!SWAP MIDDLE CONCAT TO CHANGE SHEETS!!
creds_gs = os.path.join(os.getenv("HOME"), "PycharmProjects/OCLCTools/my_wskey.json")
gsheet = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/"
    + "GHSEET_ID_GOES_HERE_IN_QUOTES"
    + "/export?gid=0&format=csv"
)

# Create a dictionary of OCLC/MMS pairs
# Critical for overlaying the imported records into ILS
id_dict = pd.Series(gsheet.MMSID.values, index=gsheet.OCLCID).to_dict()
print(id_dict)

oclc_numbers = [o for o in gsheet["OCLCID"]]
token = get_token()

# Loop over oclc numbers and make calls to API for each
with MetadataSession(authorization=token, agent="de12@rice.edu") as session:

    for o in oclc_numbers:
        # !!Create an exception wrapper
        # Preview through matchMARC should minimize errors
        response = session.get_full_bib(oclcNumber=o)

        # Convert responses from XML then parse in pymarc
        data = BytesIO(response.content)
        bib = parse_xml_record(data)

        # Add
        bib.add_ordered_field(my_590)

        # Change
        # Create a mmsID variable, remove old 001, add new 001 w/ variable
        # Calls on dictionary key:value pairs created earlier
        mms001 = Field(tag="001", data=str(id_dict.get(bib["001"].value())))
        bib.remove_fields("001")
        bib.add_ordered_field(mms001)

        # Remove
        bib.remove_fields("015", "016", "017", "019", "029",
                          "055", "060", "070", "072", "082",
                          "084", "263", "856", "938"
                          )
        # Test if ind2 == 7, remove field if so
        subjects = bib.get_fields("600", "610", "611", "630", "647",
                                  "648", "650", "651", "653", "654",
                                  "655", "656", "657", "658", "662"
                                  )
        for s in subjects:
            if "7" in s.indicator2:
                bib.remove_field(s)

        print(bib)

        # Write to a MARC21 file
        with open("retrieved_bibs.mrc", "ab") as out:
            out.write(bib.as_marc())
