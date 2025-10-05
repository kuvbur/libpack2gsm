import os

import sys
import re

class SourceLocationInfo:
  def __init__(self,controldir):
    self.controldir = controldir
    self.read()

  def isMainSource(self):
    return self.ismainsrc

  def getProjectID(self):
    return self.projectid

  def getFullSrcSpec(self):
    return self.fullsrcspec

  def isCVSSrc (self):
    return os.path.isfile(os.path.join(self.controldir,'CVS','Root'))

  def isSVNSrc (self):
    return os.path.isfile(os.path.join(self.controldir,'.svn','entries'))

  def getSVNSourceInfo(self):
    result = {}
    # * read url
    fileSVN = open (os.path.join(self.controldir,'.svn','entries'))
    url = None
    line = fileSVN.readline()
    while line and not url :
      m = re.match('.*url=\"(.+\/Control)\".*', line)
      if m:
        url = m.group(1)
      line = fileSVN.readline()
    fileSVN.close()
    # * read tag/server
    if url:
      result['fullsrcspec'] = url
      m = re.match('.*\/([^\/]+)\/Control',url)
      if m:
        result['tag'] = m.group(1)
        result['branch'] = m.group(1)
      m = re.match('.*\/\/([^\/]+)\/',url)
      if m:
         result['server'] = m.group(1)
    return result

  def getCVSSourceInfo(self):
    result = {}
    # * read server
    fileRoot = open(os.path.join(self.controldir,'CVS','Root'))
    server = fileRoot.readline().rstrip('\n\r')
    m = re.match(':sspi:(.+)',server)
    if m:
      server = m.group(1)
    m = re.match(':pserver:[^@]+\@(.+)',server)
    if m:
      server = m.group(1)
    fileRoot.close()
    result['server'] = server
    # * read tag/branch
    tag = ''
    if os.path.isfile(os.path.join(self.controldir,'CVS','Tag')):
      fileTag = open (os.path.join(self.controldir,'CVS','Tag'))
      tag = fileTag.readline().rstrip('\n\r')
      result['tag'] = tag
      fileTag.close()
      m = re.match('T(.+)',tag)
      if m:
        result['branch'] = m.group(1)
    result['fullsrcspec'] = server + ' ' + tag
    return result


  def ReadPerforceDepotPath (self):
    depotPath = ""
    try:
      fileObj = open (os.path.join (self.controldir, "Config", "SCM", "PerforceInfo.txt"), "r")
    except IOError:
      return ""
    for line in fileObj:
      regExpPath = re.search ("\$File\:\s+(//\S+)\s+\$", line)
      if regExpPath != None:
        depotPath = regExpPath.group (1)
        depotPath = re.sub ("[\\/]Control[\\/].*", "", depotPath)
    return depotPath


  def getPerforceSourceInfo(self, depotPath):
    result = {}
    branch = ""
    if depotPath == "//Development/Main":
      branch = "Main"
    else:
      regExp = re.search ("/([^/]+)/([^/]+)$", depotPath)
      if regExp != None:
        branch = regExp.group (2)
        if branch == "Main":
          branch = regExp.group (1)
    if branch != "":
      result["branch"] = branch
    return result


  def read(self):
    ''' reads the following fileds:
        projectid       - None or the id of the project of the current source
        fullsrcspec     - Full specification of the built source
        ismainsource    - Is this the official source?! '''
    self.projectid = None
    self.fullsrcspec = None
    self.ismainsrc = False
    srcinfo = {}
    isPerforce = False
    if self.isCVSSrc():
      srcinfo = self.getCVSSourceInfo ()
    elif self.isSVNSrc():
      srcinfo = self.getSVNSourceInfo ()
    else:
      depotPath = self.ReadPerforceDepotPath ()
      if depotPath != "":
        isPerforce = True
        srcinfo = self.getPerforceSourceInfo (depotPath)
        srcinfo["fullsrcspec"] = depotPath
        srcinfo['server'] = "ac-devserver"
      else:
        print 'SourceLocationInfo: unknown scm method (not CVS or .svn) - assuming main branch'
        srcinfo['server'] = 'archicad-repository'
    if (srcinfo['server'].find('archicad-repository') >= 0) or (srcinfo['server'].find('leopard') >= 0):
      self.ismainsrc = True

    releaseBranch = re.search ("^//Releases/", srcinfo["fullsrcspec"]) != None
    versionBranch = re.search ("/Main$", srcinfo["fullsrcspec"]) != None

    if srcinfo['server'].find('ac-devserver') >= 0 and (srcinfo["branch"] == "Main" or releaseBranch or versionBranch):
      self.ismainsrc = True
    if srcinfo.has_key('branch'):
      if isPerforce == False:
        m = re.match('b-(.+)',srcinfo['branch'])
        if m:
          self.projectid = m.group(1)
      else:
        if srcinfo["branch"] != "Main" and not releaseBranch and not versionBranch:
          self.projectid = srcinfo["branch"]
        self.fullsrcspec = srcinfo["fullsrcspec"]
    if not self.ismainsrc and self.projectid == None:
      self.projectid = 'xxx'
