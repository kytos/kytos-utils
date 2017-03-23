##########
Change log
##########

This is a log of changes made to the *kytos-utils* project.

Version b1 - bethania - 2017-03-24
**********

Added
=====

- License, Readme and Authors file.

- etc/skel files.

- Command line tool to manage the kytos napps-server.
  - May now use the command line to:
    - Create new NApps.
    - Install/remove Napps.
    - Enable/disable NApps.
    - List available NApps.
    - Search for NApps in the server.
    - Upload NApps to the server.
  - Help is available for command line tools.

- Requirements file.

Changed
=======

- Setup script installs all requirements.

- Updated to Python 3.6.

- Several bug fixes.

- Separate CLI code from NApps code.

Security
========

- Authentication for NApps upload process.

- Improve in log messages.
