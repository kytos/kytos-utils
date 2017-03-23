##########
Change log
##########

This is a log of changes made to the *kytos-utils* project.

Version: "bethania" beta1 (2017.1b1)
*************************************

Added
=====

- License, Readme and Authors files.

- etc/skel files, with templates to create all the necessary NApp files when
  executing :code:`kytos napps create`.

- Command line tool to manage the kytos NApps. A set of commands to help
  managing NApps.

  - May now use the command line to:
 
    - Create new NApps.
    - Install NApps created locally or from the NApps server.
    - Enable/disable installed NApps.
    - List installed / enabled NApps.
    - Search for NApps in the NApps server.
    - Upload NApps to the server.

  - Help is available for command line tools. Appending :code:`--help` to the
    end of a command displays useful information about it.

- Requirements file listing all the necessary software for *kytos-utils* to
  run.

Changed
=======

- Setup script now installs all the requirements during the setup process.
  There is no need to worry about them beforehand.

- Updated to Python 3.6 to make use of advantages of the new version.

- Several bug fixes.

- Separate CLI code from NApps code: refactored code to make clear what is
  related to the command line tools and what is related to the kytos NApps.

Security
========

- Authentication for NApps upload process - there is need for an account in
  the `NApps server <https://napps.kytos.io>`__ to upload any NApp.

- Clean and descriptive log messages.
