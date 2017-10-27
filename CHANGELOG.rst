##########
Change log
##########
This is a log of changes made to the *kytos-utils* project.

[UNRELEASED] - Under development
********************************
Added
=====
- Commands to handle the Kytos Controller
  (`kytos controller <start/stop/status>`).

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

[2017.2b2] - "chico" beta2 - 2017-10-20
***************************************
Added
=====
- `kytos napps prepare` command to generate openapi.yml skeleton file

Changed
=======
- Dependency installation/update for devs:
  `pip install -Ur requirements/dev.txt`. To use cloned kytos repos as
  dependencies, reinstall that repos with `pip install -e .` in the end.
- Improvements on napps dependencies management.

Fixed
=====
- Linter issues.
- Unneeded running Kytosd requirement.

[2017.2b1] - "chico" beta1 - 2017-09-19
***************************************
Added
=====
- Version tags - now NApps fully support the <username>/<nappname>:<version> format.
- Create an OpenAPI skeleton based on NApp's rest decorators.

Changed
=======
- NApps will now install other NApps listed as dependencies.
- Do not require a running kytosd for some commands.
- Yala substitutes Pylama as the main linter checker.
- Requirements files updated and restructured.

Fixed
=====
- Some test features.
- Some bug fixes.


[2017.1] - 'bethania' - 2017-07-06
**********************************
Fixed
=====
- NApp skel to match changes in Kytos


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
