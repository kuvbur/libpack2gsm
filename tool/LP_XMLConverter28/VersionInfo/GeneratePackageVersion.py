#!/usr/bin/python


###############################################################################
# Ignore pylint messages:

# Invalid name
# pylint: disable-msg=C0103

# Line too long
# pylint: disable-msg=C0301

# Missing docstring
# pylint: disable-msg=C0111

# Bad identation
# pylint: disable-msg=W0311

# Comma not followed by a space
# pylint: disable-msg=C0324

# Found indentation with tabs instead of spaces
# pylint: disable-msg=W0312

# Catch "Exception"
# pylint: disable-msg=W0703

###############################################################################


''' GeneratePackageVersion script

Generates the following XML file:

<packageversion>
  <buildnumber>1235</buildnumber>
[ <projectbuildnumber>12</projectbuildnumber> ]
[ <internalproject>[X-666|ACX]</internalproject> ]
[ <lastintegration>123456</lastintegration> ]
  <codename>Sindbad</codename>
  <product_family_id>archicad</product_family_id>
  <shortversionstring>9</shortversionstring>
  <versionstring>9.0</versionstring>
  <gslangcode>INT</gslangcode>
[ <privatebuild/> ]
  <platform>Win32</platform>
[ <cpuarchitecture>x86-64</cpuarchitecture> ]
  <prefspostfix>Wright INT X-666 26</prefspostfix>
  [ <prefspostfix>Wright INT 26</prefspostfix> ]
  [ <prefspostfix>Wright INT D1</prefspostfix> ]
[ <guid>{01234567-ABCD-0123-ABCD-0123456789AB}<guid> ]
[ <supersedes-lib name="Library Name" guid="{01234567-ABCD-0123-ABCD-0123456789AB}"> ]
[ <updates-lib>Library Name</updates-lib> ]
[ <updates-guid>{01234567-ABCD-0123-ABCD-0123456789AB}</updates-guid> ]
[ <needs-lib>Library Name</needs-lib> ]
[ <needs-guid>{01234567-ABCD-0123-ABCD-0123456789AB}</needs-guid> ]
[ <collapse-branches/> ]
</packageversion>

'''


import sys
import os
import getopt
import re
import VersInfoXMLHandler
import SourceLocationInfo
import argparse

import xml.sax
import xml.etree.ElementTree as ET
from xml.dom import minidom

parser = argparse.ArgumentParser (description='Generates ProductVersion.xml')
parser.add_argument ('--buildnumfile',          required=True)
parser.add_argument ('--projectbuildnumfile')
parser.add_argument ('--lastintegrationfile')
parser.add_argument ('--gslangcode',            required=True)
parser.add_argument ('--platform',              required=True)
parser.add_argument ('--cpuarchitecture')
parser.add_argument ('--gsprodtype',            required=True)
parser.add_argument ('--output',                required=True)
parser.add_argument ('--versinfoxml',           required=True)
parser.add_argument ('--controldir')
parser.add_argument ('--nonlocalizedtemplate')
parser.add_argument ('--guidfile')
parser.add_argument ('--updatesandneedslibfile')
parser.add_argument ('--supersedesfile')
parser.add_argument ('--privatebuild',     action='store_true')
parser.add_argument ('--collapsebranches', action='store_true')
parser.add_argument ('--debugversion',     action='store_true')
parser.add_argument ('--testversion',      action='store_true')
parser.add_argument ('--islibrary',        action='store_true')


def KeepOnlyKeysWithNonEmptyValuesIn (theDict):
  # Refactoring compatibility: mainArgs is originally expected
  # not to have a key if an argument was not passed
  result = {}

  for key, value in theDict.items ():
    if value is not None:
      result[key] = value

  return result

mainArgs = KeepOnlyKeysWithNonEmptyValuesIn (vars (parser.parse_args ()))

class ReadNonlocalizedTemplate (xml.sax.handler.ContentHandler):
  def __init__ (self, path):
    xml.sax.handler.ContentHandler.__init__ (self)
    self.nonReferenceBuild = False
    xml.sax.parse (path, self)

  def startElement (self, name, _attr):
    if name == 'nonreferencebuild':
      self.nonReferenceBuild = True

  def hasNonReferenceBuild (self):
    return self.nonReferenceBuild

def CreatePreferencesPostfix (state,
                              codename,
                              shortversion,
                              language,
                              productType,
                              relname,
                              internalproject,
                              privatebuild,
                              buildnum,
                              projectBuildnum):
  ''' returns the postfix string of the preferences:
        final format (from beta and up, official builds):
            9.0.0 INT v1 STUD
        development format (before beta or private builds):
            Nautilus INT STUD 26
        project format (for internal project's)
            Nautilus INT D-012 STUD 26
  '''
  productTypestr = ''
  if productType != 'FULL':
    productTypestr = ' ' + productType

  if projectBuildnum == 0:
    buildnumStr = "%d" % (buildnum)
  else:
    buildnumStr = "%d.%d" % (buildnum, projectBuildnum)

  if (codename == "BIMcloud"):
    ''' state? '''
    if not internalproject:
      return '%s %s.%s' % (codename, shortversion, buildnumStr)
    else:
      return '%s %s %s.%s' % (codename, internalproject, shortversion, buildnumStr)
  else:
    if (state != "development") and not privatebuild and not internalproject:
      return shortversion + ' ' + language + ' ' + relname + productTypestr
    elif not internalproject:
      return codename + ' ' + language + productTypestr + ' %s' % buildnumStr
    else:
      return codename + ' ' + language + ' ' + internalproject + productTypestr + ' %s' % buildnumStr

def readBuildNum (path, primary = True):
  if primary:
    numfile = open (path)
    num = int (numfile.readline ())
    numfile.close ()
  else:
    try:
      numfile = open (path)
      num = int (numfile.readline ())
      numfile.close ()
    except Exception:
      num = 0
  return num

def formatGUID (guid_, path_):
  guid_ = "{" + guid_.rstrip ("\r\n") + "}"
  if len (guid_) != 38:
    raise Exception ("Error! GeneratePackageVersion.py error: wrong guid length in file: " + path_)
  if guid_ != guid_.upper ():
    raise Exception ("Error! GeneratePackageVersion.py error: lower case guid found in file: " + path_)
  if guid_ == "{00000000-0000-0000-0000-000000000000}":
    raise Exception ("Error: GeneratePackageVersion.py error: NULL guid found in file: " + path_)
  return guid_

def isosx ():
  return os.name == 'posix'
def iswin32 ():
  return os.name == 'nt'

def readVersionInfo (path, isLibrary):
  if os.path.isfile (path):
    info = VersInfoXMLHandler.VersionXMLParser (path)
    codename = info.getValue ('codename')
    product_family_id = info.getValue ('product_family_id')

    if isLibrary:
        version = info.getValue ('libraryversionstring')
    else:
        version = info.getValue ('fullversionstring')

    updateversion = info.getValue ('updateversion')
    hotfixversion = info.getValue ('hotfixversion')

    shortversion = VersInfoXMLHandler.getShortVersion (version)
    state = info.getValue ('state')
    if iswin32 ():
      releasename = info.getValue ('releasename_win')
    if isosx ():
      releasename = info.getValue ('releasename_mac')
    if not codename:
      raise Exception ('Expected: GS_VERS_PROD_CODENAME in %s' % path)
    if not product_family_id:
      raise Exception ('Expected: GS_VERS_PROD_FAMILY_ID in %s' % path)
    if not version:
      raise Exception ('Expected: GS_VERS_PROD_VERSIONSTRING in %s' % path)
    if not shortversion:
      raise Exception ('Expected: GS_VERS_PROD_SHORT_VERSIONSTRING in %s' % path)
    return {'codename':codename, 'product_family_id':product_family_id, 'version':version, 'updateversion':updateversion, 'hotfixversion':hotfixversion, 'shortversion':shortversion, 'state':state, 'releasename':releasename}
  else:
    raise Exception (path + ' is missing!')


class ProductVersionXmlBuilder:

  def __init__ (self):
    self.root = ET.Element ('productversion')

  def withTextElement (self, name, text):
    elem = ET.SubElement (self.root, name)
    elem.text = str (text)
    return self

  def withEmptyElement (self, name):
    ET.SubElement (self.root, name)
    return self

  def withEmptyElementIfAffirmativeInDict(self, theDict, dictKey, elementName = None):
    if elementName is None:
      elementName = dictKey

    if dictKey in theDict and theDict[dictKey]:
      return self.withEmptyElement (elementName)

    return self

  def withTextElementFromDict (self, theDict, dictKey, elementName = None):
    if elementName is None:
      elementName = dictKey

    return self.withTextElement (elementName, theDict[dictKey])

  def withTextElementFromDictIfAny (self, theDict, dictKey, elementName = None):
    if dictKey in theDict:
      return self.withTextElementFromDict (theDict, dictKey, elementName)
    
    return self

  def withSupersedesElement (self, name, guid):
    element = ET.SubElement (self.root, 'supersedes-lib')
    element.set ('name', name)
    element.set ('guid', guid)
    return self

  def build (self):
    withXmlDeclaration = minidom.parseString (ET.tostring (self.root)).toprettyxml (indent="  ")
    return '\n'.join(withXmlDeclaration.split('\n')[1:])

  def dumpToFile (self, path):
    with open (path, 'w') as fileObj:
      fileObj.write (self.build ())
    
    return self

def DoWritePackageVersion (args):
  pvXmlBuilder = ProductVersionXmlBuilder ()  

  projectid = None
  if args.get ('controldir'):
    sli = SourceLocationInfo.SourceLocationInfo (args['controldir'])
    if not sli.isMainSource ():
      projectid = sli.getProjectID ()
      m = re.match ('Team-(AC[0-9]+)', projectid)
      if m:
        projectid = m.group (1)
  
  buildnum        = readBuildNum (args['buildnumfile'])
  projectBuildnum = readBuildNum (args['projectbuildnumfile'], False)
  info            = readVersionInfo (args['versinfoxml'], args['islibrary'])

  pvXmlBuilder.withTextElement ('buildnumber', buildnum)

  if projectBuildnum > 0:
    pvXmlBuilder.withTextElement ('projectbuildnumber', projectBuildnum)
  if projectid:
    pvXmlBuilder.withTextElement ('internalproject', projectid)
    if "lastintegrationfile" in args:
      if os.path.exists (args["lastintegrationfile"]):
        with open (args["lastintegrationfile"]) as lastIntegrationFileObj:
          pvXmlBuilder.withTextElement ('lastintegration', lastIntegrationFileObj.read ())

  pvXmlBuilder                                                                                    \
    .withTextElementFromDict      ( info, dictKey='codename'                                              ) \
    .withTextElementFromDict      ( info, dictKey='product_family_id',   elementName='product_family_id'  ) \
    .withTextElementFromDict      ( info, dictKey='version',             elementName='versionstring'      ) \
    .withTextElementFromDict      ( info, dictKey='updateversion',       elementName='updateversionstring') \
    .withTextElementFromDict      ( info, dictKey='hotfixversion',       elementName='hotfixversionstring') \
    .withTextElementFromDict      ( info, dictKey='shortversion',        elementName='shortversionstring' ) \
    .withTextElementFromDict      ( args, dictKey='platform'                                              ) \
    .withTextElementFromDictIfAny ( args, dictKey='cpuarchitecture'                                       ) \
    .withTextElementFromDict      ( args, dictKey='gslangcode',          elementName='gslanguage'         ) \
    .withTextElementFromDict      ( args, dictKey='gsprodtype'                                            )
  
  pvXmlBuilder                                                                                    \
    .withEmptyElementIfAffirmativeInDict (args, dictKey='privatebuild'                          )

  if args['debugversion']:
    pvXmlBuilder.withEmptyElement ('debug')
  elif args['testversion']:
    pvXmlBuilder.withEmptyElement ('test')

  if 'nonlocalizedtemplate' in args:
    rnc = ReadNonlocalizedTemplate (args['nonlocalizedtemplate'])
    if rnc.hasNonReferenceBuild ():
      pvXmlBuilder.withEmptyElement ('nonreferencebuild')

  else:
    pvXmlBuilder.withEmptyElement ('nonreferencebuild')

  preferencesPostFix = CreatePreferencesPostfix (info['state'],
                                                info['codename'],
                                                info['version'],
                                                args['gslangcode'],
                                                args['gsprodtype'],
                                                info['releasename'],
                                                projectid,
                                                args['privatebuild'],
                                                buildnum,
                                                projectBuildnum)

  pvXmlBuilder.withTextElement ('prefspostfix', preferencesPostFix)

  if 'guidfile' in args:
    guidFilePath = args['guidfile']

    with open (guidFilePath) as numfile:
      pvXmlBuilder.withTextElement ('guid', formatGUID (numfile.readline (), guidFilePath))

  if 'updatesandneedslibfile' in args:

    updatesAndNeedsLibFilePath = args['updatesandneedslibfile']

    with open (updatesAndNeedsLibFilePath) as datfile:
      
      pvXmlBuilder.withTextElement ('updates-lib',  datfile.readline ().rstrip ("\r\n"))
      updatesGuid = formatGUID (datfile.readline (), updatesAndNeedsLibFilePath)
      pvXmlBuilder.withTextElement ('updates-guid', updatesGuid)
      
      pvXmlBuilder.withTextElement ('needs-lib',    datfile.readline ().rstrip ("\r\n"))
      needsGuid = formatGUID (datfile.readline (),   updatesAndNeedsLibFilePath)
      pvXmlBuilder.withTextElement ('needs-guid',   needsGuid)

      if updatesGuid == needsGuid:
        raise Exception ("Error! GeneratePackageVersion.py error: equal needs-guid and updates-guid found!")


  if 'supersedesfile' in args:
    with open (args['supersedesfile']) as supfile:
      num = int (supfile.readline ())
      for i in range (num):
        pvXmlBuilder.withSupersedesElement (name=supfile.readline ().rstrip (),
                                           guid="{" + supfile.readline ().rstrip () + "}")

  if args['collapsebranches']:
    pvXmlBuilder.withEmptyElement ('collapse-branches')

  pvXmlBuilder.dumpToFile (args['output'])

def PrintDiagnosticInfo():
  print 'I was called from this directory:'
  print os.getcwd ()
  print 
  print 'I was called with these args:'
  print sys.argv
  print 

try:
  DoWritePackageVersion (mainArgs)

except KeyError as e:
  print('KeyError encountered')
  print('\nHint: a KeyError could mean that a command line argument is missing')
  print('(e. g. --{})\n'.format(str(e)[1:-1]))
  
  PrintDiagnosticInfo()
  raise

except Exception:
  PrintDiagnosticInfo()
  raise


