# FSM Web Uploader

FSM Web Uploader is an FTP-based application for managing and automating the upload of the website files produced by the FS Manager software used in judging figure skating competitions.

## Functionality

The core functionality of this program is as follows:
- Allows secure connections to FTP sites that support FTP over TLS, in addition to allowing insecure connections when this is not available.
- Monitors the website output folder of FS Manager for new files and uploads new files as they are made available
- Stores the state of the folder between runs to avoid reuploading duplicate files.
- Makes arbitrary edits to the uploaded HTML files as defined in provided replacements file, and does so non-destructively by making the edits in memory only.
- Selectively uploads pages displaying judging panels, accommodating last minute changes without having to manually manage the contents of the website output directory.

## Use

The program is designed to be as simple to use as possible. Simply fill the information fields and click run! The fields are as follows:
- **Hostname:** the hostname or IP address of the FTP server (e.g., bisresults.co.uk)
- **Port:** the port of the FTP server (e.g., 21)
- **Username:** your FTP username
- **Password:** your FTP account password (NOTE: saving the config of your setup save the password in plain text. Store your files securely!)
- **Timeout duration:** the timeout duration of the server in minutes. See the footnote for an explanation of this functionality.
- **Local website folder:** the folder that FSM outputs your site files to. The directory will have the same name as the competition code of the competition you are running.
- **Remote directory:** the folder on the FTP server that your files will be uploaded to. This folder MUST exist before using this program.
- **Edits file:** a JSON file specifying edits to be made to the HTML files when they are uploaded. The keys specify the text to be replaced, and the values the text it will be replaced with.
- **Save file:** a JSON file saving the state of the folder at the start and end of each program run. This can be either a path to an existing file or a path to save a new file to.
- **Copy PDFs?:** This option specifies whether the program should search for PDFs to upload to the site. Currently, only Judges Details Per Skater are supported. 
- **FS Manager Folder:** The root directory of FS Manager that the program will search for PDFs. The default location is C:\SwissTiming\OVR\FSManager.

**Note:** as there is no universal keepalive standard amongst FTP servers, this program uses the broadest possible approach of sending a file (.keep) consisting of a single byte of data to the remote server one minute before the specified timeout duration.

Examples of the configuration and replacement files are in the `templates` folder of this repository.

## Installation

There are two methods to install this program:
- Install the pre-packaged binary: for this, simply download the folder and unzip it where you want to keep the application.
- Install from source: to do this, UV is the recommended method. A series of example commands is below.
  - Clone the git archive
  - Run `main.py` using UV (see below)

```PowerShell
git clone "https://github.com/rghskate/fsm-web-uploader"
cd fsm-web-uploader
uv run gui.py
```

## Licenses

This application is released under a GPLv3 license, the text of which can be found bundled with this application, or else at this address: https://www.gnu.org/licenses/gpl-3.0.en.html.

The licenses of the libraries this application uses can be found in LICENSES.md, or in the licenses window of the application.

# DISCLAIMER

FS Manager is the sole property of Swiss Timing. This application does not in any way replicate or replace the functionality or purpose of FS Manager. This application is in no way endorsed by Swiss Timing.