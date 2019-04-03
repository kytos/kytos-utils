########
Overview
########

|Experimental| |Tag| |Release| |License| |Build| |Coverage| |Quality|

This is a command line interface (cli) for `Kytos SDN Platform
<https://kytos.io/>`_. With these utilities you can interact with Kytos daemon
and manage Network Applications (NApps) on your controller.

QuickStart
**********

Installing
==========

We use python3.6. So in order to use this software please install python3.6
into your environment beforehand.

We are doing a huge effort to make Kytos and its components available on all
common distros. So, we recommend you to download it from your distro repository.

But if you are trying to test, develop or just want a more recent version of
our software no problem: Download now, the latest release (it still a beta
software), from our repository:

First you need to clone *kytos-utils* repository:

.. code-block:: shell

   $ git clone https://github.com/kytos/kytos-utils.git

After cloning, the installation process is done by standard `setuptools` install
procedure:

.. code-block:: shell

   $ cd kytos-utils
   $ sudo python3.6 setup.py install

Usage
*****

In order to execute *kytos* command line, please run:

.. code-block:: shell

   $ kytos --help

Authors
*******

For a complete list of authors, please open ``AUTHORS.rst`` file.

Contributing
************

If you want to contribute to this project, please read `Kytos Documentation
<https://docs.kytos.io/kytos/contributing/>`__ website.

License
*******

This software is under *MIT-License*. For more information please read
``LICENSE`` file.

.. |Experimental| image:: https://img.shields.io/badge/stability-experimental-orange.svg
.. |Tag| image:: https://img.shields.io/github/tag/kytos/kytos-utils.svg
   :target: https://github.com/kytos/kytos-utils/tags
.. |Release| image:: https://img.shields.io/github/release/kytos/kytos-utils.svg
   :target: https://github.com/kytos/kytos-utils/releases
.. |Tests| image:: https://travis-ci.org/kytos/kytos-utils.svg?branch=master
   :target: https://travis-ci.org/kytos/kytos-utils
.. |License| image:: https://img.shields.io/github/license/kytos/kytos-utils.svg
   :target: https://github.com/kytos/kytos-utils/blob/master/LICENSE
.. |Build| image:: https://scrutinizer-ci.com/g/kytos/kytos-utils/badges/build.png?b=master
  :alt: Build status
  :target: https://scrutinizer-ci.com/g/kytos/kytos-utils/?branch=master
.. |Coverage| image:: https://scrutinizer-ci.com/g/kytos/kytos-utils/badges/coverage.png?b=master
  :alt: Code coverage
  :target: https://scrutinizer-ci.com/g/kytos/kytos-utils/?branch=master
.. |Quality| image:: https://scrutinizer-ci.com/g/kytos/kytos-utils/badges/quality-score.png?b=master
  :alt: Code-quality score
  :target: https://scrutinizer-ci.com/g/kytos/kytos-utils/?branch=master
