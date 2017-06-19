##########
Change log
##########
This is a log of changes made to the *kytos-utils* project.

[UNRELEASED] - Under development
********************************
Added
=====

Changed
=======

Deprecated
==========

Removed
=======

Fixed
=====

Security
========


[2017.1b3] - "bethania" beta3 - 2017-06-16
******************************************
Added
=====
- Commands to enable/disable all installed NApps
  (`kytos napps <enable/disable> all`).

Changed
=======
- Install and enable NApps based on Kytos instance. `kytos-utils` will request
  the configuration loaded by kytos before managing NApps.

Removed
=======
- Support for NApp management whithout a Kytos running instance.

Fixed
=====
- A few bug fixes.


[2017.1b2] - "bethania" beta2 - 2017-05-05
******************************************
Added
=====
- :code:`kytos users register` command can be used to register a new user in
  the NApps server.
- Now under MIT license.

Changed
=======
- skel templates updated to match changes in logging and kytos.json.
- Improved tests and style check for developers, and added continuous
  integration.

Deprecated
==========
- kytos.json 'author' attribute is being replaced by 'username' due to context,
  and is deprecated. It will be removed in future releases.

Removed
=======
- kytos.json 'long_description' attribute is no longer necessary nor available.
  The detailed description shall now be in README.rst.

Fixed
=====
- Now creates the NApps directory structure when it does not exist.
- Pypi package is fixed and working.
- Several bug fixes.


[2017.1b1] - "bethania" beta1 - 2017-03-24
******************************************
Added
=====
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

Changed
=======
- Setup script now installs all the requirements during the setup process.
  There is no need to worry about them beforehand.
- Updated to Python 3.6.
- Several bug fixes.
- Separate CLI code from NApps code: refactored code to make clear what is
  related to the command line tools and what is related to the kytos NApps.
- Clean and descriptive log messages.

Security
========
- Authentication for NApps upload process - there is need for an account in
  the `NApps server <https://napps.kytos.io>`__ to upload any NApp.
