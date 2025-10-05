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
  <shortversionstring>9</shortversionstring>
  <versionstring>9.0</versionstring>
  <gslangcode>INT</gslangcode>
[ <privatebuild/> ]
  <platform>Win32</platform>
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

import xml.sax


try:
  opts, mainArgs = getopt.getopt(sys.argv[1:], '',
	['help',
	 'buildnumfile=',
	 'projectbuildnumfile=',
	 'lastintegrationfile=',
	 'gslangcode=',
     'platform=',
	 'gsprodtype=',
	 'output=',
	 'versinfoxml=',
     'controldir=',
     'nonlocalizedtemplate=',
     'privatebuild',
     'guidfile=',
     'updatesandneedslibfile=',
     'supersedesfile=',
     'collapsebranches',
     'debugversion',
     'testversion',
     'islibrary',
	 ])
except getopt.error, msg:
  print msg
  print "for help use --help"
  sys.exit(2)


mainArgs = {}

for o, a in opts:
  if o in ["--help"]:
    print __doc__
    sys.exit(0)
  elif o in ['--privatebuild']:
    mainArgs['privatebuild'] = True
  elif o in ['--buildnumfile']:
    mainArgs['buildnumfile'] = a
  elif o in ['--projectbuildnumfile']:
    mainArgs['projectbuildnumfile'] = a
  elif o in ['--lastintegrationfile']:
    mainArgs['lastintegrationfile'] = a
  elif o in ['--gslangcode']:
    mainArgs['gslangcode'] = a
  elif o in ['--platform']:
    mainArgs['platform'] = a
  elif o in ['--gsprodtype']:
    mainArgs['gsprodtype'] = a
  elif o in ['--versinfoxml']:
    mainArgs['versinfoxml'] = a
  elif o in ['--output']:
    mainArgs['output'] = unicode(a, 'utf-8')
  elif o in ['--controldir']:
    mainArgs['controldir'] = a
  elif o in ['--nonlocalizedtemplate']:
    mainArgs['nonlocalizedtemplate'] = a
  elif o in ['--guidfile']:
    mainArgs['guidfile'] = a
  elif o in ['--updatesandneedslibfile']:
    mainArgs['updatesandneedslibfile'] = a
  elif o in ['--supersedesfile']:
    mainArgs['supersedesfile'] = a
  elif o in ['--collapsebranches']:
    mainArgs['collapsebranches'] = True
  elif o in ['--debugversion']:
    mainArgs['debugversion'] = True
  elif o in ['--testversion']:
    mainArgs['testversion'] = True
  elif o in ['--islibrary']:
    mainArgs['islibrary'] = True
  else:
    raise Exception('O:%s A:%s' % (o, a))

class ReadNonlocalizedTemplate(xml.sax.handler.ContentHandler):
  def __init__(self, path):
    xml.sax.handler.ContentHandler.__init__(self)
    self.nonReferenceBuild = False
    xml.sax.parse(path, self)
  def startElement(self, name, _attr):
  	if name == 'nonreferencebuild':
  		self.nonReferenceBuild = True
  def hasNonReferenceBuild(self):
  	return self.nonReferenceBuild

def CreatePreferencesPostfix(state,
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

def readBuildNum(path, primary = True):
  if primary:
    numfile = open(path)
    num = int(numfile.readline())
    numfile.close()
  else:
    try:
      numfile = open(path)
      num = int(numfile.readline())
      numfile.close()
    except Exception:
      num = 0
  return num

def formatGUID(guid_, path_):
  guid_ = "{" + guid_.rstrip("\r\n") + "}"
  if len(guid_) != 38:
    raise Exception("Error! GeneratePackageVersion.py error: wrong guid length in file: " + path_)
  if guid_ != guid_.upper():
    raise Exception("Error! GeneratePackageVersion.py error: lower case guid found in file: " + path_)
  if guid_ == "{00000000-0000-0000-0000-000000000000}":
    raise Exception("Error: GeneratePackageVersion.py error: NULL guid found in file: " + path_)
  return guid_

def writeLibraryGuidTag(path_, fileObj):
  if not os.path.isfile(path_):
    raise Exception("Error: GeneratePackageVersion.py error: Missing file: " + path_)

  numfile = open(path_)
  _guid = formatGUID(numfile.readline(), path_)
  numfile.close()
  fileObj.write('  <guid>%s</guid>\n' % _guid)


def writeUpdatesAndNeedsLibraryTags(path_, fileObj):
  if not os.path.isfile(path_):
    raise Exception("Error: GeneratePackageVersion.py error: Missing file: " + path_)

  datfile = open(path_)

  _updatesLibrary = datfile.readline().rstrip("\r\n")
  fileObj.write('  <updates-lib>%s</updates-lib>\n' % _updatesLibrary)
  _updatesGuid = formatGUID(datfile.readline(), path_)
  fileObj.write('  <updates-guid>%s</updates-guid>\n' % _updatesGuid)

  _needsLibrary = datfile.readline().rstrip("\r\n")
  fileObj.write('  <needs-lib>%s</needs-lib>\n' % _needsLibrary)
  _needsGuid = formatGUID(datfile.readline(), path_)
  fileObj.write('  <needs-guid>%s</needs-guid>\n' % _needsGuid)

  if _updatesGuid == _needsGuid:
    raise Exception("Error! GeneratePackageVersion.py error: equal needs-guid and updates-guid found!")
  return


def writeSupersedesTag(path_, fileObj):
  if not os.path.isfile(path_):
    raise Exception("Error: GeneratePackageVersion.py error: Missing file: " + path_)

  supfile = open(path_)
  num = int(supfile.readline())
  for i in range(num):
    name = supfile.readline().rstrip()
    guid = "{" + supfile.readline().rstrip() + "}"
    fileObj.write('  <supersedes-lib name="%s" ' % name)
    fileObj.write('guid="%s"/>\n' % guid)


def isosx():
  return os.name == 'posix'
def iswin32():
  return os.name == 'nt'

def readVersionInfo(path, isLibrary):
  if os.path.isfile(path):
    info = VersInfoXMLHandler.VersionXMLParser(path)
    codename = info.getValue('codename')

    if isLibrary:
        version = info.getValue('libraryversionstring')
    else:
        version = info.getValue('fullversionstring')

    shortversion = VersInfoXMLHandler.getShortVersion(version)
    state = info.getValue('state')
    if iswin32():
      releasename = info.getValue('releasename_win')
    if isosx():
      releasename = info.getValue('releasename_mac')
    if not codename:
      raise Exception('Expected: GS_VERS_PROD_CODENAME in %s' % path)
    if not version:
      raise Exception('Expected: GS_VERS_PROD_VERSIONSTRING in %s' % path)
    if not shortversion:
      raise Exception('Expected: GS_VERS_PROD_SHORT_VERSIONSTRING in %s' % path)
    return {'codename':codename, 'version':version, 'shortversion':shortversion, 'state':state, 'releasename':releasename}
  else:
    raise Exception(path + ' is missing!')



def DoWritePackageVersion(args):
  projectid = None
  if args.has_key('controldir'):
    sli = SourceLocationInfo.SourceLocationInfo(args['controldir'])
    if not sli.isMainSource ():
      projectid = sli.getProjectID()
      m = re.match('Team-(AC[0-9]+)', projectid)
      if m:
        projectid = m.group(1)
  buildnum = readBuildNum(args['buildnumfile'])
  projectBuildnum = readBuildNum(args['projectbuildnumfile'], False)
  info = readVersionInfo(args['versinfoxml'], args.has_key ('islibrary'))
  if os.path.isfile(args['output']):
    os.unlink(args['output'])
  tmppath = args['output'] + '.tmp'
  tmppathDir = os.path.dirname(tmppath)
  fileObj = open(tmppath, 'w')
  fileObj.write('<productversion>\n')
  fileObj.write('  <buildnumber>%d</buildnumber>\n' % buildnum)
  if projectBuildnum > 0:
    fileObj.write('  <projectbuildnumber>%d</projectbuildnumber>\n' % projectBuildnum)
  if projectid:
    fileObj.write('  <internalproject>%s</internalproject>\n' % projectid)
    if args.has_key ("lastintegrationfile"):
      if os.path.exists (args["lastintegrationfile"]):
        lastIntegrationFileObj = open (args["lastintegrationfile"])
        fileObj.write('  <lastintegration>%s</lastintegration>\n' % lastIntegrationFileObj.read ())
        lastIntegrationFileObj.close ()
  fileObj.write('  <codename>%s</codename>\n' % info['codename'])
  fileObj.write('  <versionstring>%s</versionstring>\n' % info['version'])
  fileObj.write('  <shortversionstring>%s</shortversionstring>\n' % info['shortversion'])
  fileObj.write('  <platform>%s</platform>\n' % args['platform'])
  fileObj.write('  <gslanguage>%s</gslanguage>\n' % args['gslangcode'])
  fileObj.write('  <gsprodtype>%s</gsprodtype>\n' % args['gsprodtype'])
  if args.has_key('privatebuild'):
    fileObj.write('  <privatebuild/>\n')

  if args.has_key ("debugversion"):
    fileObj.write ("  <debug/>\n")
  elif args.has_key ("testversion"):
    fileObj.write ("  <test/>\n")

  if args.has_key('nonlocalizedtemplate'):
  	rnc = ReadNonlocalizedTemplate (args['nonlocalizedtemplate'])
  	if rnc.hasNonReferenceBuild():
  	  fileObj.write('  <nonreferencebuild/>\n')
  else:
    fileObj.write('  <nonreferencebuild/>\n')
  fileObj.write('  <prefspostfix>%s</prefspostfix>\n' % CreatePreferencesPostfix(info['state'], info['codename'], info['version'], args['gslangcode'], args['gsprodtype'], info['releasename'], projectid, args.has_key('privatebuild'), buildnum, projectBuildnum))

  if args.has_key('guidfile'):
    writeLibraryGuidTag(args['guidfile'], fileObj)

  if args.has_key('updatesandneedslibfile'):
    writeUpdatesAndNeedsLibraryTags(args['updatesandneedslibfile'], fileObj)

  if args.has_key('supersedesfile'):
    writeSupersedesTag(args['supersedesfile'], fileObj)

  if args.has_key('collapsebranches'):
    fileObj.write('  <collapse-branches/>\n')
  fileObj.write('</productversion>\n')
  fileObj.close()
  os.rename(tmppath, args['output'])

DoWritePackageVersion(mainArgs)
