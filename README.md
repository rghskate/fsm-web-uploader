# FSM Web Uploader

FSM Web Uploader is an FTP-based application for managing and automating the upload of the website files produced by the FS Manager software used in judging figure skating competitions.

## Motivation

This program was created to solve the rather specific problem of judging and technical panels changing at short notice due to unforeseen circumstances leading to communication difficulties during figure skating events. It has since evolved into a more general tool for uploading FS Manager generated files, which serve well for ISU competitions but leave something to be desired with regards to federated competitions.

## Functionality

The program comes with both a CLI and GUI, depending on user preference. Functionality between the two versions is effectively identical. The main features are as follows:

- Monitors folder of HTML files created by FS Manager and uploads changes as they are made by comparing file hashes.
- Copies PDFs from the FS Manager directory to the upload directory as they are generated, and replaces them with the latest version in case of changes.
- Makes arbitrary edits to the uploaded HTML files as defined in the provided replacements CSV (e.g., removing references to Solo Dance necessary when using older versions of FS Manager to run solo dance competitions). This is preferable to editing the templates used by FS Manager as doing so can lead to breaking the generation of the pages.
  - For a template of an appropriate file to define replacements in.

## Installation

Currently, only the GUI portion of the application is distributed as a packaged application, and only for Windows (although FS Manager only runs on Windows so it's probably the only place that you'd ever want to use it anyway). To use it, unzip the folder to wherever you want to keep the application and run the executable.

To run the application from source using UV, the below sequence of commands in PowerShell should work:

```PowerShell
git clone "https://github.com/rghskate/fsm-web-uploader"
cd fsm-web-uploader
uv run gui.py
```

## Licenses

This application is released under a GPLv3 license, the text of which can be found bundled with this application, or else at this address: https://www.gnu.org/licenses/gpl-3.0.en.html

This application is written in Python, which is licensed under the [Python Software Foundation License](https://docs.python.org/3/license.html).

This application relies on the following third party modules and their corresponding licenses:

| Module | License |
|---|---|
| [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) | [MIT](https://opensource.org/license/mit) |
| [LXML](https://lxml.de/) | [BSD-3-Clause](https://github.com/lxml/lxml/blob/master/doc/licenses/BSD.txt) |
| [Pandas](https://pandas.pydata.org/) | [BSD-3-Clause](https://github.com/pandas-dev/pandas/blob/main/LICENSE) |
| [PyQt6](https://doc.qt.io/qtforpython-6) | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html) |

The author of this software can be contacted at [robert.hayes@iceskating.org.uk](mailto:robert.hayes@iceskating.org.uk).

# DISCLAIMER

FS Manager is the sole property of Swiss Timing. This application does not in any way replicate or replace the functionality or purpose of FS Manager. This application is in no way endorsed by Swiss Timing.
