# FSM Web Uploader: a simple program for uploading the web files produced by FS Manager software used in figure skating judging.
#     Copyright (C) 2025  Robert Hayes

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
import shutil
from ftplib import FTP
import hashlib
import configparser

class Configuration:
    '''
    Container for configuration options for program.
    '''
    def __init__(self) -> None:
        self.host = None
        self.port = None
        self.user = None
        self.password = None
        self.remote_dir = None
        self.local_dir = None
        self.swiss_timing = None
        self.replace = None
        self.move_pdf = None
        self.save_file = None

    def from_ini(self,config_filepath) -> None:
        '''
        Read INI file to Configuration object.
        '''
        config_obj = configparser.RawConfigParser()
        config_obj.read(config_filepath)

        self.host = config_obj.get('FTP','Hostname')
        self.port = config_obj.get('FTP','Port')
        self.user = config_obj.get('FTP','Username')
        self.password = config_obj.get('FTP','Password')

        self.remote_dir = config_obj.get('Directories','Remote')
        self.local_dir = os.path.abspath(os.path.normpath(config_obj.get('Directories','Local')))

        try:
            self.replace = os.path.abspath(os.path.normpath(config_obj.get('Edits','ReplacementList')))
            if self.replace == "":
                self.replace = None
        except configparser.NoOptionError:
            self.replace = None
        
        try:
            self.swiss_timing = config_obj.get('Directories','SwissTiming')
            if self.swiss_timing == "":
                self.swiss_timing = r'C:\SwissTiming\OVR\FSManager'
        except configparser.NoOptionError:
            self.swiss_timing = r'C:\SwissTiming\OVR\FSManager'

        try:
            self.save_file = config_obj.get('Management','SaveFile')
            if self.save_file == "":
                self.save_file = None
        except configparser.NoOptionError:
            self.save_file = None

        try:
            self.move_pdf = config_obj.getboolean('Management','MovePDF')
            if self.move_pdf == "":
                self.move_pdf = False
        except (configparser.NoOptionError, ValueError):
            self.move_pdf = False
    
    def to_ini(self, path:str):
        '''
        Write configuration object to INI file.
        '''
        config = configparser.RawConfigParser()
        config['FTP'] = {
                'Hostname':self.host,
                'Port':self.port,
                'Username':self.user,
                'Password':self.password
            }
        config['Directories'] = {
                'Remote':self.remote_dir,
                'Local':self.local_dir,
                'SwissTiming':self.swiss_timing,
            }
        config['Edits'] = {
                'ReplacementList':self.replace,
            }
        config['Management'] = {
                'MovePDF':self.move_pdf,
                'SaveFile':self.save_file,
            }
        if path[-4:] != '.ini':
            path += '.ini'
        with open(path,'w') as f:
            config.write(f)

    def __str__(self) -> str:
        return f'''Current config:

--- FTP ---
Hostname: {self.host}
Port: {self.port}
Username: {self.user}
Password: {self.password}

--- Directories ---
Local directory: {self.local_dir}
Remote directory: {self.remote_dir}
Swiss Timing Directory: {self.swiss_timing}

--- Edits ---
Text replacement file: {self.replace}

--- Management ---
Move PDFs to website folder: {self.move_pdf}
Save file location: {self.save_file}
'''

def return_from_generator_gui(gen, emitter_target, args:list):
    '''
    Exhausts generator and returns any return value, sending pyqtSignals of yielded text.
    '''
    itr = gen(*args)
    while True:
        try:
            string, _ = next(itr)
            try:
                emitter_target.output_signal.emit(string)
            except TypeError:
                emitter_target.output_signal.emit(f'{string}')
        except StopIteration as e:
            return_value = e.value
            break
    return return_value

def return_from_generator_cli(gen, args:list):
    '''
    Exhausts generator and returns and return value, printing to stdout any yielded text.
    '''
    itr = gen(*args)
    while True:
        try:
            string, overwrite = next(itr)
            if overwrite is True:
                overprint(string)
            else:
                print(string)
        except StopIteration as e:
            return_value = e.value
            break
    return return_value

def flatten_list(lst):
    def flatten(lst):
        for item in lst:
            if isinstance(item, list):
                yield from flatten(item)
            else:
                yield item
    return list(flatten(lst))

def copy_pdfs(swiss_timing_folder,local_dir):
    dirname = os.path.join(swiss_timing_folder,'Export',os.path.basename(local_dir),'PDF')
    file_paths = []
    for root, _, files in os.walk(dirname):
        for file in files:
            abs_path = os.path.abspath(os.path.join(root, file))
            file_paths.append(abs_path)
    target_files = ['JudgesDetailsperSkater.pdf']
    pdfs = [pdf for pdf in file_paths if any(target_file in pdf for target_file in target_files)]
    
    currently_present_pdfs = [file for file in os.listdir(local_dir) if any(target_file in file for target_file in target_files)]

    for file in pdfs:
        if os.path.basename(file) not in currently_present_pdfs:
            yield f'Copying "{file}" to "{local_dir}"...', True
            shutil.copyfile(os.path.normpath(file), os.path.normpath(os.path.join(local_dir,os.path.basename(file))))
        elif (os.path.basename(file) in currently_present_pdfs) and (hash_sha256(file) != hash_sha256(os.path.basename(file))):
            yield f'{hash_sha256(file)}\n{hash(os.path.basename(file))}', True
            yield f'Copying latest version of "{file}" to "{local_dir}"...', True
            shutil.copyfile(os.path.normpath(file), os.path.normpath(os.path.join(local_dir,os.path.basename(file))))
    
def overprint(content):
    print(end='\x1b[2K')
    print(content, end='\r')

def ftp_connect(hostname,user,password,remote_dir,port="",stop_sequence:str='Ctrl+C'):
    yield f'Connecting to FTP site {hostname}:{port} as {user}...', False

    if port != "":
        port = "".join([':',port])

    try:
        ftp = FTP(f'{hostname}{port}')
    except Exception as e:
        yield 'Connection to remote failed with the following error:\n', False
        yield e, False
        yield 'Trying connecting without port.', False
        try:
            ftp = FTP(f'{hostname}')
        except Exception as e:
            yield '\nPlease review your connection settings in your environment file.', False
            raise ConnectionError()
    
    try:
        ftp.login(user=user, passwd=password)
    except Exception as e:
        yield 'Authentication failed with the following error:\n', False
        yield e, False
        yield '\nPlease review your connection settings in your environment file.', False
        raise ConnectionError()
    
    yield 'Connection successful! Server returned following welcome message:\n', False
    yield ftp.getwelcome(), False
    
    try:
        ftp.cwd(remote_dir)
    except Exception as e:
        yield 'Could not find directory on remote. Server returned following error:\n', False
        yield e, False
        yield '\nPlease review your connection settings in your environment file.', False
        raise ConnectionError()
    
    yield '\nMonitoring local directory for changes...', False
    yield f'\nTo close connection, press {stop_sequence}.\n', False

    return ftp

def replace_text(filepath:str, old_text:list[str], new_text:list[str]):
    with open(filepath,'r') as f:
        page = f.read()
    
    for i, entry in enumerate(old_text):
        page = page.replace(entry, new_text[i])

    with open(filepath, 'w') as f:
        f.write(page)

def hash_sha256(filepath:str):
    try:
        with open(filepath,'rb') as f:
            file_hash = hashlib.sha256()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except FileNotFoundError:
        return None

def upload_updated_files(ftp:FTP, current_filetable:pd.DataFrame, old_filetable:pd.DataFrame):
    old_filetable = old_filetable.reset_index(drop=True)
    update_counter = 0
    brand_new_files = current_filetable.loc[~current_filetable['filepaths'].isin(old_filetable['filepaths']),'filepaths']
    comparable_files = current_filetable.loc[current_filetable['filepaths'].isin(old_filetable['filepaths']),:].reset_index(drop=True)

    if len(brand_new_files) > 0:
        for path in brand_new_files:
            with open(path,'rb') as file:
                ftp.storbinary(f'STOR {path}', file)
                yield f'Updated {path} on remote', True
            update_counter += 1

    for i in range(0,len(comparable_files)):
        if comparable_files.loc[i,'hashes'] != old_filetable.loc[i,'hashes']:
            with open(comparable_files.loc[i,"filepaths"],'rb') as file:
                ftp.storbinary(f'STOR {comparable_files.loc[i,"filepaths"]}', file)
                yield f'Updated {comparable_files.loc[i,"filepaths"]} on remote', True
            update_counter += 1
    
    return update_counter

def verify_file_status(index_page:str):
    copyright_notices = [r'&copy;',r'<a href="http://www.isu.org">International Skating Union</a>', r'All Rights Reserved.']

    if not all(substring in index_page for substring in copyright_notices):
        return False
    else:
        return True

def find_results_table(html_soup:BeautifulSoup, tag_name:str='table', attributes:dict={'width':'70%'}, target_table_index:int=0) -> list:
    results_table = html_soup.find_all(tag_name,attributes)[target_table_index]
    return results_table

def build_segment_table(results_table: BeautifulSoup):
    rows:list = results_table.find_all('tr')
    rows.pop(0)

    segments = []
    date = None
    for row in rows:
        cells = row.find_all('td')
        if 'TabHeadWhite' in f'{row}' and '<th>' not in f'{row}':
            date = cells[0].text.strip()
        elif len(cells) > 0:
            time = cells[1].text.strip()
            name = cells[2].text.strip()
            link_name = cells[3].text.strip()
            link = cells[3].find_all('a',href=True)[0].get('href')

            date_obj = datetime.strptime(f'{date} {time}','%d.%m.%Y %H:%M:%S')

            segments.append([date_obj,name,link_name,link])
            
    segments = pd.DataFrame(segments,columns=['date_obj','category','segment','segment_link'])
    segments.loc[:,'segment_judges_link'] = segments.loc[:,'segment_link'].str.replace('.htm','OF.htm')

    return segments

def update_ftp_server(ftp:FTP, filetable_current:pd.DataFrame, config:Configuration,
                      replacements:pd.DataFrame, segments:pd.DataFrame, time_last_update:datetime,
                      manual_time:datetime|None=None,
                      cli:bool=True, uploader_instance=None):
    '''
    Checks local filelist and pushes changes to FTP server based on checksum values of html files.
    '''
    yield 'Checking for changes...', True
    filetable_previous = filetable_current
    for msg, dest in copy_pdfs(config.swiss_timing, config.local_dir):
        yield msg, dest
    local_filelist = pd.Series(os.listdir('.'))

    if config.replace is not None:
        for file in local_filelist:
            if os.path.splitext(file)[1] == '.htm':
                replacements.fillna('',inplace=True)
                replace_text(file,replacements['OldText'],replacements['NewText'])

    if manual_time is not None:
        test_time = manual_time
    else:
        test_time = datetime.now()
    files_to_ignore = segments['segment_judges_link'][segments['date_obj'] > test_time]

    filetable_current = pd.DataFrame({'filepaths':local_filelist[~local_filelist.isin(files_to_ignore)],
                                    'hashes':local_filelist[~local_filelist.isin(files_to_ignore)].apply(hash_sha256)})

    if cli is True:
        update_counter = return_from_generator_cli(upload_updated_files, [ftp, filetable_current, filetable_previous])
    else:
        update_counter = return_from_generator_gui(upload_updated_files, uploader_instance, [ftp, filetable_current, filetable_previous])

    if update_counter == 0:
        yield f"Time since last update = {str(datetime.now()-time_last_update).split('.')[0]}", True
    else:
        yield f'Updated {update_counter} on last round.', True
        time_last_update = datetime.now()
            
    return filetable_current, time_last_update