import xml.sax
import xml.sax.handler
import re

class VersionXMLParser(xml.sax.handler.ContentHandler):
  def __init__(self,path):
    xml.sax.handler.ContentHandler.__init__(self)
    self.dict = {}
    self.transformer = {
                    'state':{'beta':'1 /* beta */','alpha':'2 /* alpha */','development':'3 /* development */','release':'0 /* release */'}
                 }
    xml.sax.parse(path,self)


  def startElement(self,name,attr):
    self.chars = ''

  def endElement(self,name):
    if self.transformer.has_key(name) and not self.chars in self.transformer[name].keys():
      raise Exception('Error in XML: %s=%s should be one of %s' % (name, self.chars, self.transformer[name].keys()))
    self.dict[name] = self.chars

  def characters(self,characters):
    self.chars = self.chars + characters

  def getValue(self,name):
    return self.dict[name]

  def getTransformedValue(self,name):
    if self.transformer.has_key(name):
      return self.transformer[name][self.dict[name]]
    else:
      return self.getValue(name)

  def hasKey(self,name):
    return self.dick.has_key(name)


def getShortVersion(arg):
  m = re.match('([0-9]+)\.([0-9]+)\.([0-9]+)',arg)
  #if m.group(3) == '0':
  #  if m.group(2) == '0':
  return m.group(1)
  #  else:
  #    return m.group(1)+'.'+m.group(2)
  #else:
  #  return arg

def ParseCommand(command,keys):
  def DO_LEN(arg,keys):
    return len(arg)
  def DO_STR(arg,keys):
    return '"%s"' % arg
  def DO_READ_FROM_VERSXML(arg,keys):
    return keys.getValue(arg)
  def DO_VERSMAINNUM(arg,keys):
    return re.match('([0-9]+)\.([0-9]+)\.([0-9]+)',arg,).group(1)
  def DO_VERSSUBNUM(arg,keys):
    return re.match('([0-9]+)\.([0-9]+)\.([0-9]+)',arg).group(2)
  def DO_VERSREVNUM(arg,keys):
    return re.match('([0-9]+)\.([0-9]+)\.([0-9]+)',arg).group(3)
  def DO_STATEASNUMBER(arg,keys):
    decoder = {'beta':'1 /* beta */','alpha':'2 /* alpha */','development':'3 /* development */','release':'0 /* release */'}
    return decoder[arg]
  def DO_SHORTVERS(arg,keys):
    return getShortVersion(arg)
  cmdtable = {'LEN':DO_LEN,'STR':DO_STR,'READ_FROM_VERSXML':DO_READ_FROM_VERSXML,'STATEASNUMBER':DO_STATEASNUMBER,
			  'VERSMAINNUM':DO_VERSMAINNUM,'VERSSUBNUM':DO_VERSSUBNUM,'VERSREVNUM':DO_VERSREVNUM,'SHORTVERS':DO_SHORTVERS}
  re_value = re.compile('\"([a-z\_]+)\"')
  re_command = re.compile('([A-Z\_]+)\((.+)\)')
  if re_value.match(command):
    return re_value.match(command).group(1)
  else:
    m = re_command.match(command)
    cmd = m.group(1)
    return cmdtable[cmd](ParseCommand(m.group(2),keys),keys)


class VersionSubsituter:
  def __init__(self,path):
     self.parser = VersionXMLParser (path)
     self.re_line = re.compile('(.*\s)\<([^>]+)\>(\s.*)')
     self.re_line = re.compile('(.*\s)\<([^>]+)\>(|\s.*)')

  def parse(self,line):
     m = self.re_line.match(line)
     if m:
       return m.group(1)+str(ParseCommand(m.group(2),self.parser))+m.group(3)
     else:
       return line
