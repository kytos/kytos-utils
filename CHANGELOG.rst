##########
Change log
##########
This is a log of changes made to the *kytos-utils* project.

UNRELEASED - Under development
******************************
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

[2018.2b2] - "ernesto" beta2 - 2018-10-15
*****************************************
Added
=====
 - Added flag --meta to create a new NApp with meta-package structure.

Fixed
=====
 - Fixed bug when creating NApp (#190)
 - Fixed some linter erros

[2018.2b1] - "ernesto" beta1 - 2018-09-06
*****************************************
Nothing has changed since 2018.1rc1

[2018.1rc1] - "dalva" release candidate - 2018-06-29
****************************************************
Fixed
=====
- Fixed small bug

[2018.1b3] - "dalva" beta3 - 2018-06-15
***************************************
Added
=====
- `kytos napps reload <username>/<napp_name>` will reload the NApp code
- `kytos napps reload all` command to update the NApp code of all NApps

Changed
=======
- Improved log error messages

[2018.1b2] - "dalva" beta2 - 2018-04-20
**************************************
Added
=====
- `kytos napps create` will create the ui folder [`ui/k-toolbar`,
  `ui/k-menu-bar`, `k-info-panel`] when creating a new Napp structure
- `kytos web update <version>` command to update the Kytos Web User Interface
  with a specific version

Fixed
=====
- Fix some docstring and comments

[2018.1b1] - "dalva" beta1 - 2018-03-09
**************************************
Nothing has changed since 2017.2

[2017.2] - "chico" stable - 2017-12-21
**************************************
Nothing has changed since 2017.2rc1

[2017.2rc1] - "chico" release candidate 1 - 2017-12-15
******************************************************
Added
=====
- `kytos web update` command to update the Kytos Web User Interface to the
  latest version.


[2017.2b2] - "chico" beta2 - 2017-12-01
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
