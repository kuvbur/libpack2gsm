# -*- coding: utf-8 -*-
import pathlib
import subprocess
import shutil
import os
from download_and_unzip import GetLP_XMLConverters
from lxml import etree
import json
import re

code_list = ['Script_1D', 'Script_3D', 'Script_2D','Script_PR','Script_UI','Script_VL','Script_FWM','Script_BWM', 'Comment','Keywords']
def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise

def prepfolder(folder):
    if folder.exists():
        shutil.rmtree(folder, ignore_errors=False,
                      onerror=handleRemoveReadonly)
    folder.mkdir(parents=True)
    return folder

def run_shell_command(command_line):
    try:
        result = subprocess.call (command_line)
    except (OSError) as exception:
        print('Exception occured: ' + str(exception))
        return False
    else:
        # no exception was raised
        print('Subprocess finished')
    return True

def getpackageinfo(lcf_dir, language):
    info = {}
    try:
        parser = etree.XMLParser(strip_cdata=False)
        root = etree.parse(str(lcf_dir /'package.info'), parser)
        croot = root.getroot()
        info['lcfPath'] = croot.find('LCFPath').attrib['lcfPath']
        info['displayName'] = croot.attrib['displayName']
    except Exception as e:
        print(e)
    filenamejson = None
    symbolStringsjson = None
    try:
        parser = etree.XMLParser(strip_cdata=False)
        root = etree.parse(str(lcf_dir /'localizationData.info'), parser)
        croot = root.getroot()
        LocalizedPackageNamesPath = croot.find('LocalizedPackageNamesPath').text
        PathNameTables = croot.find('Dictionaries')
        if PathNameTables is not None:
            for p in PathNameTables:
                if p.attrib['language'] == language:
                    if 'fileName' in p.attrib['type']: 
                        filenamejson = p.attrib['path']
                    if 'symbolStrings' in p.attrib['type']: 
                        symbolStringsjson = p.attrib['path']
            if filenamejson is None:
                for p in PathNameTables:
                    if p.attrib['language'] == 'INT':
                        if 'fileName' in p.attrib['type']: 
                            filenamejson = p.attrib['path']
                        if 'symbolStrings' in p.attrib['type']: 
                            symbolStringsjson = p.attrib['path']
    except Exception as e:
        print(e)
    if LocalizedPackageNamesPath is not None:
        localizedPackageNamesFile = open(lcf_dir/LocalizedPackageNamesPath, 'r', encoding="utf-8")
        localizedPackageNamesData = json.load(localizedPackageNamesFile)
        if language in localizedPackageNamesData['LocalizedPackageNames']:
            info['PackageName'] = localizedPackageNamesData['LocalizedPackageNames'][language]
        else:
            if 'INT' in localizedPackageNamesData['LocalizedPackageNames']:
                info['PackageName'] = localizedPackageNamesData['LocalizedPackageNames']['INT']
        localizedPackageNamesFile.close()
    if filenamejson is not None:
        pattern = (
            r'msgctxt\s+"(.*?)"\s+'
            r'msgid\s+"(.*?)"\s+'
            r'msgstr\s+"(.*?)"'
        )
        filename = {}
        with open(lcf_dir/filenamejson, encoding='utf-8') as f:
            content = f.read()
            matches = re.findall(pattern, content, re.DOTALL)
            for msgctxt, msgid, msgstr in matches:
                if msgid != msgstr:
                    filename[msgid] = msgstr
        if len(filename)>0: info['filename'] = filename
    if symbolStringsjson is not None:
        paramname = {}
        with open(lcf_dir/symbolStringsjson, encoding='utf-8') as f:
            content = f.read()
            blocks = re.split(r'\n\s*\n', content)
            for block in blocks:
                # Поиск всех комментариев в блоке
                comments = re.findall(r'^(#.*)', block, re.MULTILINE)
                # Поиск тройки ключей
                match = re.search(
                    r'msgctxt\s+"(.*?)"\s+msgid\s+"(.*?)"\s+msgstr\s+"(.*?)"', block, re.DOTALL)
                if match:
                    msgctxt, msgid, msgstr = match.groups()
                    if msgid != msgstr:
                        for c in comments:
                            c = c.replace('#: ', '')
                            c = c.replace('.gsm', '')
                            if c not in paramname:
                                paramname[c] = {}
                            if msgctxt not in paramname[c]:
                                paramname[c][msgctxt] = {}
                            if msgid not in paramname[c][msgctxt]:
                                paramname[c][msgctxt][msgid] = msgstr
        if len(paramname)>0: info['paramname'] = paramname
    return info

def translate_xml(fname, param):
    try:
        parser = etree.XMLParser(strip_cdata=False)
        root = etree.parse(str(fname), parser)
        croot = root.getroot()
    except Exception as e:
        print(e)
        return
    if 'Parameter Description' in param:
        try:
            prm = croot.find('ParamSection').find('Parameters')
            for child in prm:
                if 'Parameter Description' in param:
                    if child.find('Description') is not None:
                        tt = child.find('Description').text.strip('"')
                        if tt in param['Parameter Description']:
                            child.find('Description').text = etree.CDATA('"' + param['Parameter Description'][tt] + '"')
                if 'Parameter Value' in param:
                    if child.find('Value') is not None:
                        tt = child.find('Value').text.strip('"')
                        if tt in param['Parameter Value']:
                            if child.tag == 'String':
                                child.find('Value').text = etree.CDATA('"' + param['Parameter Value'][tt] + '"')
                            else:
                                child.find('Value').text = param['Parameter Value'][tt]
        except Exception as e:
            print(e)
    if 'Script String' in param:
        try:
            for code in code_list:
                prm = croot.find(code)
                if prm is not None:
                    prmtext = prm.text
                    if code == 'Keywords' and 'Library Part Keyword' in param:
                        prmtext = list(param['Library Part Keyword'].items())[0]
                    if code == 'Comment' and 'Library Part Description' in param:
                       prmtext = list(param['Library Part Description'].items())[0]
                    if code != 'Keywords' and code != 'Comment':
                        for p in param['Script String']:
                            prmtext = prmtext.replace('"' + p + '"', '"' + param['Script String'][p] + '"')
                            prmtext = prmtext.replace("'" + p + "'", "'" + param['Script String'][p] + "'")
                            prmtext = prmtext.replace("`" + p + "`", "`" + param['Script String'][p] + "`")
                    prm.text = etree.CDATA('"' + prmtext + '"')
        except Exception as e:
            print(e)
    etree.indent(root, space="\t")
    txt = etree.tostring(root, encoding='UTF-8', xml_declaration=True).decode()
    txt = txt.replace('[""', '["')
    txt = txt.replace('""]', '"]')
    txt = txt.replace('["]', '[""]')
    with open(fname, 'tw', encoding='utf-8') as f:
        f.write(txt)

def gsm2lcf(lcf_dir, libpack, display_name, lcf_name, convt):
    lcf = lcf_dir/ f"{display_name}.lcf"
    param = [f'{convt}', 'createcontainer',f'{lcf}','-compress','9',
              f'{libpack/lcf_name.split(".")[0]}']
    if run_shell_command(param):
        return lcf
    else:
        print ("Error on gsm2lcf")
        return None
    
def xml2gsm(temp_dir, libpack, convt):
    old_gsm_dir = prepfolder(temp_dir /libpack.parent.name.split(".")[0]/"gsm25")
    param = [f'{convt}', 'x2l','-l','CYR',
             f'{libpack}', f'{old_gsm_dir}']
    if run_shell_command(param):
        return old_gsm_dir
    else:
        print ("Error on xml2gsm")
        return None

def gsm2xml(temp_dir, libpack, convf):
    xml_dir = prepfolder(temp_dir /libpack.parent.name.split(".")[0]/"from_gsm")
    param = [f'{convf}', 'l2x','-l','CYR','-compatibility','25',
             f'{libpack}', f'{xml_dir}']
    if run_shell_command(param):
        return xml_dir
    else:
        print ("gsm2xml")
        return None

def lcf2gsm(libpack, lcf_name, convf):
    gsm_dir = prepfolder(libpack.parent/"from_lcf")
    param = [f'{convf}', 'extractcontainer',
             f'{libpack/lcf_name}', f'{gsm_dir}']
    if run_shell_command(param):
        return gsm_dir
    else:
        print ("lcf2gsm")
        return None

def libpack2lcf(temp_dir, libpack, convf):
    lcf_dir = prepfolder(temp_dir /libpack.name.split(".")[0]/"from_libpack")
    param = [f'{convf}', 'extractpackage',
             f'{libpack.absolute()}', f'{lcf_dir}']
    if run_shell_command(param):
        return lcf_dir
    else:
        print ("libpack2lcf")
        return None

def main(from_version, to_version, language, source_path, target_path, merge_lcf):
    curr_dir = pathlib.Path(__file__).parent.absolute()
    if source_path is None:
        source_path = curr_dir / 'libpack'
    else:
        source_path = pathlib.Path(source_path)
    if target_path is None:
        target_path = curr_dir / 'lcf'
    else:
        target_path = pathlib.Path(target_path)
    temp_dir = curr_dir / 'temp'
    prepfolder(temp_dir)
    convf = GetLP_XMLConverters(from_version, curr_dir / 'tool')
    convt = GetLP_XMLConverters(to_version, curr_dir / 'tool')
    paths = sorted(pathlib.Path(source_path).glob('**/*.libpack'))
    if merge_lcf : full_lcf = prepfolder(temp_dir / 'full_lcf')
    for libpack in paths:
        lcf_dir = libpack2lcf(temp_dir, libpack, convf)
        if lcf_dir is not None:
            info = getpackageinfo(lcf_dir, language)
            if info['lcfPath'] is not None:
                gsm_dir = lcf2gsm(lcf_dir, info['lcfPath'], convf)
        if gsm_dir is not None:
            xml_dir = gsm2xml(temp_dir, gsm_dir, convf)
            if 'paramname' in info:
                for f in info['paramname']:
                    for p in sorted(pathlib.Path(xml_dir).glob('**/'+f+'.xml')):
                        translate_xml(p, info['paramname'][f])
            if 'filename' in info:
                for f in info['filename']:
                    for p in sorted(pathlib.Path(xml_dir).glob('**/'+f+'.xml')):
                        p.rename(p.parent / f'{info["filename"][f]}.xml')
        if xml_dir is not None:
            old_gsm_dir = xml2gsm(temp_dir, xml_dir, convt)
        if old_gsm_dir is not None:
            if merge_lcf : shutil.copytree(old_gsm_dir/info['displayName'].split(".")[0], full_lcf/info['PackageName'])
            lcf25_dir = gsm2lcf(target_path, old_gsm_dir, info['displayName'], info['lcfPath'],convt)
    if merge_lcf:
        param = [f'{convt}', 'createcontainer',str(target_path/'full_lcf_25.lcf'),'-compress','9',
                f'{full_lcf}']
        run_shell_command(param)
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=False,
                        onerror=handleRemoveReadonly)

if __name__ == "__main__":
    main("28", "25", "RUS", None, None, False)
