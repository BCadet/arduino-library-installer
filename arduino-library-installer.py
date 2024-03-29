import json
import requests
import argparse
import os
import tarfile
import platform
import sys
import shutil
import gzip
import zipfile

def gunzip_shutil(source_filepath, dest_filepath, block_size=65536):
    with gzip.open(source_filepath, 'rb') as s_file, \
            open(dest_filepath, 'wb') as d_file:
        shutil.copyfileobj(s_file, d_file, block_size)

class arduinoLibraryInstaller():

    library_index = ...
    arduinoSdkPath = ''
    sdk_json = ...

    _download_path = '/staging/libraries/'

    def __init__(self, arduinoSdk):
        self.arduinoSdkPath = arduinoSdk
        if(not os.path.isdir(self.arduinoSdkPath + self._download_path)):
            os.makedirs(self.arduinoSdkPath + self._download_path)

    def get_library_index(self):
        file = requests.get('https://downloads.arduino.cc/libraries/library_index.json.gz').content
        with open(str(self.arduinoSdkPath + '/library_index.json.gz'), 'wb') as sdkJsonFile:
            sdkJsonFile.write(file)
        gunzip_shutil(self.arduinoSdkPath + '/library_index.json.gz', self.arduinoSdkPath + '/library_index.json')
        with open(self.arduinoSdkPath + '/library_index.json', 'r') as sdkJsonFile:
            self.library_index = json.loads(sdkJsonFile.read())

    def find_library(self, libraryName, libraryVersion):
        detectedLibrary = list(filter(lambda x: x['name'] == libraryName and x['version'] == libraryVersion, self.library_index['libraries']))
        if(len(detectedLibrary) != 1):
            print('oops')
        return detectedLibrary[0]

    def download(self, library):
        url = library['url']
        print('[*] Downloading ' + library['archiveFileName'])
        with open(self.arduinoSdkPath + self._download_path + library['archiveFileName'], 'wb') as f:
            response = requests.get(url, stream=True)
            total = response.headers.get('content-length')

            if total is None:
                f.write(response.content)
            else:
                downloaded = 0
                total = int(total)
                for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                    downloaded += len(data)
                    f.write(data)
                    done = int(50*downloaded/total)
                    sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50-done)))
                    sys.stdout.flush()
        sys.stdout.write('\n')
        print('[*] Done!')

    def extractArchive(self, library, destinationPath):
        if(os.path.isdir(self.arduinoSdkPath + destinationPath + library['name'])):
            shutil.rmtree(self.arduinoSdkPath + destinationPath + library['name'])
        print('[*] Extracting ' + library['archiveFileName'] + ' to ' + destinationPath)
        zipArchive = zipfile.ZipFile(self.arduinoSdkPath + self._download_path + library['archiveFileName'])
        zipArchive.extractall(destinationPath)
        os.rename(os.path.join(destinationPath, os.path.splitext(library['archiveFileName'])[0]), os.path.join(destinationPath, library['name']))
        print('[*] Done!')

def arduino_library_installer():
    parser = argparse.ArgumentParser(description='installer for arduino librarys with dependencies')
    parser.add_argument('--library', type=str, help='the library to install')
    parser.add_argument('--library-version', type=str, default='latest', help='the library version')
    parser.add_argument('--arduino-sdk', type=str, help='arduino sdk location')
    parser.add_argument('--lib-path', type=str, help='library output path')

    args = parser.parse_args()

    installer = arduinoLibraryInstaller(args.arduino_sdk)
    installer.get_library_index()

    lib = installer.find_library(args.library, args.library_version)
    installer.download(lib)
    installer.extractArchive(lib, args.lib_path)

    
if __name__ == '__main__' :
    arduino_library_installer()