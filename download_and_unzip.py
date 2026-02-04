import os
import pathlib
import platform
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile
import requests
API_ENDPOINT = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'

convurl = {
    "28": "https://disk.yandex.ru/d/ys5eJV8SVmBTVA",
    "27": "https://disk.yandex.ru/d/C07SpAMFOXUQ9Q",
    "26": "https://disk.yandex.ru/d/Q-iPo54e0gBJiQ",
    "25": "https://disk.yandex.ru/d/gp9de0dAtIMJ7A",
    "24": "https://disk.yandex.ru/d/wNBlgOLNGUE43Q",
    "23": "https://disk.yandex.ru/d/hUE_hutcZps1Eg",
    "22": "https://disk.yandex.ru/d/XDxXlpbu3vaaQg",
    "21": "https://disk.yandex.ru/d/LYK84C1y2iAQiQ",
    "20": "https://disk.yandex.ru/d/eBP3kYmVV241Ww"}

def GetLP_XMLConverters(version: str, toolfolder):
    if toolfolder is None: toolfolder = pathlib.Path(__file__).parent / 'tool'
    if not toolfolder.exists():
        toolfolder.mkdir(parents=True)
    devKitFolderVersion = toolfolder / f'LP_XMLConverter{version}'
    if not devKitFolderVersion.exists():
        DownloadAndUnzip(convurl[version], toolfolder.absolute())
        if not devKitFolderVersion.exists():
            return None
    devKitFolderVersion = devKitFolderVersion/'WIN'/'LP_XMLConverter.EXE'
    return devKitFolderVersion.absolute()


def _extract_filename_yadisk_link(direct_link: str):
    for chunk in direct_link.strip().split('&'):
        if chunk.startswith('filename='):
            return chunk.split('=')[1]
    return None


def DownloadFromYadisk(url: str, dest: str) -> str:
    pk_request = requests.get(API_ENDPOINT.format(url))
    direct_link = pk_request.json().get('href')
    if direct_link:
        filename = _extract_filename_yadisk_link(direct_link)
        filePath = os.path.join(dest, filename)
        download = requests.get(direct_link)
        with open(filePath, 'wb') as out_file:
            out_file.write(download.content)
        print('Downloaded "{}" to "{}"'.format(url, filePath))
        return filePath
    else:
        print('Failed to download "{}"'.format(url))
        return None


def DownloadAndUnzip(url: str, dest: str):
    if 'disk.yandex' in url:
        filePath = DownloadFromYadisk(url, dest)
        fileName = filePath.split('/')[-1]
    else:
        fileName = url.split('/')[-1]
        filePath = pathlib.Path(dest, fileName)
        if filePath.exists():
            return
        print(f'Downloading {fileName}')
        urllib.request.urlretrieve(url, filePath)

    print(f'Unzipping {fileName}')
    if platform.system() == 'Windows':
        with zipfile.ZipFile(filePath, 'r') as zip:
            zip.extractall(dest)
    elif platform.system() == 'Darwin':
        subprocess.call([
            'unzip', '-qq', filePath,
            '-d', dest
        ])


if __name__ == "main":
    url = sys.argv[1]
    dest = sys.argv[2]
    DownloadAndUnzip(url, dest)
    sys.exit(0)
