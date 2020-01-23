
from xml.dom import minidom
from xml.dom.minidom import Node

import codecs

import xmltodict

import pprint

def parseXmlFile( file ):

    fileStream = codecs.open( file, "rb", "utf-8" )
    fileAsString = fileStream.read()
    fileStream.close()
    
    xmlAsDict = xmltodict.parse( fileAsString )

    return xmlAsDict


def addReqToDatabase( file, db_path ):

    xmlAsDict = parseXmlFile( file )
    pprint.pprint( xmlAsDict )


if "__main__" == __name__:

    file = "C:\\Work\\GitHub\\FAE\\FAE\\products\\VectorCAST_Requirements_Gateway\\Polarion\\reqs_for_import.xml"
    db_path = "C:\\Work\\Training\\Demo\\MinGW_WorkDir\\RGW_Polarion"

    addReqToDatabase( file, db_path )
