PizzaCutter
===========


Version v1.1.10 as of 2023-07-21 see `Changelog`_

|build_badge| |codeql| |license| |pypi|
|pypi-downloads| |black| |codecov| |cc_maintain| |cc_issues| |cc_coverage| |snyk|



.. |build_badge| image:: https://github.com/bitranox/PizzaCutter/actions/workflows/python-package.yml/badge.svg
   :target: https://github.com/bitranox/PizzaCutter/actions/workflows/python-package.yml


.. |codeql| image:: https://github.com/bitranox/PizzaCutter/actions/workflows/codeql-analysis.yml/badge.svg?event=push
   :target: https://github.com//bitranox/PizzaCutter/actions/workflows/codeql-analysis.yml

.. |license| image:: https://img.shields.io/github/license/webcomics/pywine.svg
   :target: http://en.wikipedia.org/wiki/MIT_License

.. |jupyter| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/bitranox/PizzaCutter/master?filepath=PizzaCutter.ipynb

.. for the pypi status link note the dashes, not the underscore !
.. |pypi| image:: https://img.shields.io/pypi/status/PizzaCutter?label=PyPI%20Package
   :target: https://badge.fury.io/py/PizzaCutter

.. |codecov| image:: https://img.shields.io/codecov/c/github/bitranox/PizzaCutter
   :target: https://codecov.io/gh/bitranox/PizzaCutter

.. |cc_maintain| image:: https://img.shields.io/codeclimate/maintainability-percentage/bitranox/PizzaCutter?label=CC%20maintainability
   :target: https://codeclimate.com/github/bitranox/PizzaCutter/maintainability
   :alt: Maintainability

.. |cc_issues| image:: https://img.shields.io/codeclimate/issues/bitranox/PizzaCutter?label=CC%20issues
   :target: https://codeclimate.com/github/bitranox/PizzaCutter/maintainability
   :alt: Maintainability

.. |cc_coverage| image:: https://img.shields.io/codeclimate/coverage/bitranox/PizzaCutter?label=CC%20coverage
   :target: https://codeclimate.com/github/bitranox/PizzaCutter/test_coverage
   :alt: Code Coverage

.. |snyk| image:: https://snyk.io/test/github/bitranox/PizzaCutter/badge.svg
   :target: https://snyk.io/test/github/bitranox/PizzaCutter

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/PizzaCutter
   :target: https://pypi.org/project/PizzaCutter/
   :alt: PyPI - Downloads

FUNCTION
========

A command-line utility that creates and updates software projects in any language from PizzaCutter project templates.

for the impatient, find here the latest PizzaCutter Templates:
    - `PizzaCutter default python template <https://github.com/bitranox/pct_python_default>`_


It is conceptually similar to `CookieCutter <https://cookiecutter.readthedocs.io>`_ but we want to do more and cut Pizza -
Its cookiecutter on steroids.

- cross platform
- You only need to know a very little python to use PizzaCutter (not more as You need to know about XML formatting for CookieCutter)
- works itself with Python 3.6 and above, we dont care for older versions and clutter the code.
  But templates can be in any program version or language!
- Project templates can be in any programming language or markup format:
  Python, JavaScript, Ruby, CoffeeScript, RST, Markdown, CSS, HTML, you name it.
  You can use multiple languages in the same project template, even in different encodings
- it does NOT support direct download of templates from github (now) like cookiecutter - but that is easy if someone really needs it.
- simple commandline interface:

.. code-block:: bash

    $> pizzacutter build <path_to_conf_file.py>
    $> # or even simpler if the template is prepared for it :
    $> <path_to_conf_file.py>

- or use it from python:

.. code-block:: python

   import pathlib
   import pizzacutter
   pizzacutter.build(path_conf_file=pathlib.Path('./.../.../path_to_conf_file.py'))

- Directory names and filenames can be templated. For example:

.. code-block:: bash

   {{\\PizzaCutter.repo_name}}/{{\\PizzaCutter.repo_name}}/{{\\PizzaCutter.repo_name}}.py

- Supports unlimited levels of directory nesting. (beware of possible path length limitations, especially on Travis Windows builds)
- 100% of templating is done with just (bytes) replace function. No Jinja2.

Why PizzaCutter?
================

until now, it just looks like a less mature cookiecutter, doesnt it ? But since our configuration file is python, we can do a lot of things there which we can
not
do with cookiecutter :

- Though PizzaCutter needs a little more complex `template file <https://github.com/bitranox/pct_python_default>`_ ,
  at the end You can get as complex as You like.
  Therefore You are not limited with functions or features provided by PizzaCutter, You can add or create yourself special features in the config file.
- You can (and should) inherit config files from default config files - and just change there the few things You need to change.
  In the `example <https://github.com/bitranox/pct_python_default>`_ we have decent complex config file for a python project,
  but Your default config should only inherit a small portion from that, and Your project config file should inherit from Your default config -
  it is very convenient.
  By that way a change in Your default config will be inherited by all Your project configs:

  .. code-block:: sh

        ---------------------
        | Template          |       contains all the files with patterns to replace, You can use unlimited templates in parallel !
        ---------^-----------
                 |
                 |
        ---------------------
        | master config     |       contains and probably calculate all the replacements to fill the patterns
        ---------^-----------
                 |
        ---------------------
        | default config    |       a subset of the master config, containing your default settings
        ---------^-----------
                 |
        ---------------------
        | project config    |       a subset of your default config, containing your project specific settings
        ---------^-----------

        not limited in any direction - You can stack as many layers of configs as You need,
        and You can have many configs in parallel working against the same templates


- It might sound more complicated than it is. Imagine You set Your Name and Email Adress in Your default config file -
  then You dont need to set it in Your project config anymore (unless You want to override that setting).
  By that way it is easy to manage a big number of projects with minimal effort.

- PizzaCutter is especially made to UPDATE Projects, without fuzz
- You can use multiple templates at the same time to update / create Your Project - for instance one template for the documentation,
  and another one for Your python project. Do whatever You want.
- You can mark template files if they should be updated, copied or overwritten on existing projects
- You can replace patterns in a file with the content of another file, it does not even have to be part of the template.
- You can mark text lines to be deleted when they would be empty after pattern replacement
- You can use template files in different encodings and line-endings
- You can pass string and pathlib.Path objects to the templates - allowing You a more flexible template structure
- Hooks (little programs to run before or after creation or update) are defined in the configuration file and can point to external programs.
- You can even make the configuration file executable, so it downloads the newest template itself, etc ...
- PizzaCutter informs You about unfilled patterns in Your template (if You forgot to define the pattern replacement)
- Simply define your template variables in a simple python file. This gives You all the flexibility you have ever dreamed of !!

.. code-block:: python

    # DO NOT CHANGE THIS HEADER
    from pizzacutter import PizzaCutterConfigBase

    class PizzaCutterConfig(PizzaCutterConfigBase):
        def __init__(self,
                     pizza_cutter_path_conf_file: pathlib.Path = pathlib.Path(__file__).parent.resolve(),
                     pizza_cutter_path_template_dir: Optional[pathlib.Path] = None,
                     pizza_cutter_path_target_dir: Optional[pathlib.Path] = None):
            super().__init__(pizza_cutter_path_conf_file, pizza_cutter_path_template_dir, pizza_cutter_path_target_dir)

    # Pizza Cutter Configuration, can override by cli options
            self.pizza_cutter_allow_overwrite = True
            # if it is allowed to drop files outside of the project folder - this we set default to false,
            # but can be useful to drop files on the desktop, /etc, and so on
            self.pizza_cutter_allow_outside_write = False
            self.pizza_cutter_dry_run = False
            self.pizza_cutter_quiet = False

    # User Section - do whatever You want here
    # Pizza Cutter Configuration, can override by cli options.
    # You might name Your Patterns as You like {{\\PizzaCutter. ... }}, {{LemonCutter. ... }}, {{MelonCutter. ... }}
            self.pizza_cutter_patterns['{{\\PizzaCutter.full_name}}'] = 'Robert Nowotny'
            self.pizza_cutter_patterns['{{\\PizzaCutter.email}}'] = 'bitranox@gmail.com'
            self.pizza_cutter_patterns['{{\\PizzaCutter.project.name}}'] = 'Complexity'
            self.pizza_cutter_patterns['{{\\PizzaCutter.project_short_description}}'] = 'Refreshingly simple static site generator.'
            self.pizza_cutter_patterns['{{\\PizzaCutter.release_date}}'] = '2013-07-10'
            self.pizza_cutter_patterns['{{\\PizzaCutter.year}}'] = '2013'
            self.pizza_cutter_patterns['{{\\PizzaCutter.current_version}}'] = '0.1.1'

        self.set_defaults()
        self.set_patterns()

well - that looks like a cookiecutter configuration, only a bit more complicated, so what is the difference ?
In .XML Files You just can not program. What, if for instance You want to update the "release_date"
to the current date automatically, every time You update Your project ?

With Pizzacutter its easy :

.. code-block:: python

            self.pizza_cutter_patterns['{{\\PizzaCutter.release_date}}'] = datetime.datetime.strptime(today, '%Y-%m-%d')

This is where the flexibility starts - You can dynamically calculate and assign values in the config file.

So easy, so effective, just use python for Your config.


PizzaCutter is created and maintained with PizzaCutter !

not happy with an default template ?
====================================
if you want to change some parts of a template, there is no need that You modify the default template.
(actually that would be a bad practice).

Just create another "subclassed" template and overwrite or delete files which were created by the default template You selected.
By that way, You can always inherit from the (evolving) default template, without being forced to populate
Your changes every time the default template is changed (or to become stuck with your modified template)

why not cookiecutter ?
======================
cookiecutter is nice, dont get me wrong, and its out there for a long time - so a lot of people spent time and effort to create it. It has extensive
documentation, support and user base,  which we dont have.
At the first glance, cookiecutter looks easy, but if You want to do more advanced tasks, its getting complicated - and we really see no sense to write code in
jinja templates with the limitations that come with that. An XML config file was simply not enough for us.

features of the demo python template:
=====================================
- travis.yaml is created
- cli help is automatically created (for click)
- README.rst is created automatically. only "description.rst", "usage.rst" and "CHANGES.rst" should be edited by Yourself
- master configuration file as a base for your default- and project configurations with unlimited possibilities
- for projects which are set up this way, the config files can be edited any time and the projects can be updated with one keypress.
- a shell script for local continuous testing, see ".../tests/local_testscripts/run_testloop.sh"
- a shell script to clean the project from all caches, eggs, dist and build directories, see ".../tests/local_testscripts/run_clean.sh"
- a shell script to create Your secrets (encrypted environment variables) for Travis, see ".../travis_secrets/create_secrets.sh

TODO
====

- PizzaCutter.options for delete files, directories, empty directories for easier template subclassing (though that can be done in the config files)
- function to convert or to use CookieCutter Projects - that should be easy
- maybe provide a small function for interactive settings like cookiecutter
- converting some interesting cookiecutter templates into PizzaCutter Templates
- github support (if someone needs it, we are fine at the moment with locally downloaded templates) - its easy to do, give us a note if You need it.
- yapf (python code formatter) integration or something similar, at least for setup.py generated by the default python template


STILL MISS SOMETHING ?
======================

Its simple but beautiful. Tell me if You miss anything.

----

automated tests, Github Actions, Documentation, Badges, etc. are managed with `PizzaCutter <https://github
.com/bitranox/PizzaCutter>`_ (cookiecutter on steroids)

Python version required: 3.8.0 or newer

tested on recent linux with python 3.8, 3.9, 3.10, 3.11, 3.12-dev, pypy-3.9, pypy-3.10 - architectures: amd64

`100% code coverage <https://codeclimate.com/github/bitranox/PizzaCutter/test_coverage>`_, flake8 style checking ,mypy static type checking ,tested under `Linux, macOS, Windows <https://github.com/bitranox/PizzaCutter/actions/workflows/python-package.yml>`_, automatic daily builds and monitoring

----

- `Usage`_
- `Usage from Commandline`_
- `Installation and Upgrade`_
- `Requirements`_
- `Acknowledgements`_
- `Contribute`_
- `Report Issues <https://github.com/bitranox/PizzaCutter/blob/master/ISSUE_TEMPLATE.md>`_
- `Pull Request <https://github.com/bitranox/PizzaCutter/blob/master/PULL_REQUEST_TEMPLATE.md>`_
- `Code of Conduct <https://github.com/bitranox/PizzaCutter/blob/master/CODE_OF_CONDUCT.md>`_
- `License`_
- `Changelog`_

----



Usage
-----------

In order to set up a new project You need to download the template, and edit the configuration file.

You should copy the config from the demo template to a new file and edit as needed.

Then You simply launch the config file - thats all ! (in that case You need to set the target directory in the config file)

Or You might use it like that :

.. code-block:: bash

    $> pizzacutter build <path_to_conf_file.py>
    $> # or even simpler if the template is prepared for it :
    $> <path_to_conf_file.py>




My preferred usage is, to use one template folder, and keep many configs in that folder - by that way I can update all my projects just
by launching each configuration file.


HELPERS
=======

- find version number in CHANGES.rst

.. code-block:: python

    def find_version_number_in_file(path_txt_file: pathlib.Path) -> str:
        """
        this function can be used in the PizzaCutter Template to extrect the Version Numer
        from a text file (usually CHANGES.rst)

        it finds the first line in a file, where the first non-blank character is a digit or v<digit>.
        the whole string (until ':' or EOL) is returned.

        if the version number or the file can not be found, Version 'v0.0.1a0' will be returned
        and a warning will be logged


        Parameter
        ---------
        path_txt_file
            the text file to search for

        Examples
        --------
        File content:

            some
            text
            1.2.3a0:  # or v1.2.3a0

        Output :
            1.2.3a0  # or v1.2.3a0


        >>> path_test_dir = pathlib.Path(__file__).parent.parent.parent.resolve() / 'tests'
        >>> path_test_file = path_test_dir / 'test_find_version_number_in_file.txt'
        >>> path_test_file_no_version = path_test_dir / 'test_find_version_number_in_file_no_version.txt'
        >>> path_test_file_not_existing = path_test_dir / 'non_existing_file.txt'
        >>> assert find_version_number_in_file(path_test_file) == '1.2.3a4'
        >>> assert find_version_number_in_file(path_test_file_no_version) == 'v0.0.1a0'
        >>> assert find_version_number_in_file(path_test_file_not_existing) == 'v0.0.1a0'

        """

Usage from Commandline
------------------------

.. code-block::

   Usage: pizzacutter [OPTIONS] COMMAND [ARGS]...

     create and update projects from project templates

   Options:
     --version                     Show the version and exit.
     --traceback / --no-traceback  return traceback information on cli
     -h, --help                    Show this message and exit.

   Commands:
     build  build or rebuild from CONF_FILE
     info   get program informations

Installation and Upgrade
------------------------

- Before You start, its highly recommended to update pip and setup tools:


.. code-block::

    python -m pip --upgrade pip
    python -m pip --upgrade setuptools

- to install the latest release from PyPi via pip (recommended):

.. code-block::

    python -m pip install --upgrade PizzaCutter


- to install the latest release from PyPi via pip, including test dependencies:

.. code-block::

    python -m pip install --upgrade PizzaCutter[test]

- to install the latest version from github via pip:


.. code-block::

    python -m pip install --upgrade git+https://github.com/bitranox/PizzaCutter.git


- include it into Your requirements.txt:

.. code-block::

    # Insert following line in Your requirements.txt:
    # for the latest Release on pypi:
    PizzaCutter

    # for the latest development version :
    PizzaCutter @ git+https://github.com/bitranox/PizzaCutter.git

    # to install and upgrade all modules mentioned in requirements.txt:
    python -m pip install --upgrade -r /<path>/requirements.txt


- to install the latest development version, including test dependencies from source code:

.. code-block::

    # cd ~
    $ git clone https://github.com/bitranox/PizzaCutter.git
    $ cd PizzaCutter
    python -m pip install -e .[test]

- via makefile:
  makefiles are a very convenient way to install. Here we can do much more,
  like installing virtual environments, clean caches and so on.

.. code-block:: shell

    # from Your shell's homedirectory:
    $ git clone https://github.com/bitranox/PizzaCutter.git
    $ cd PizzaCutter

    # to run the tests:
    $ make test

    # to install the package
    $ make install

    # to clean the package
    $ make clean

    # uninstall the package
    $ make uninstall

Requirements
------------
following modules will be automatically installed :

.. code-block:: bash

    ## Project Requirements
    click
    # in case we really want the latest version - otherwise we can not bootstrap
    # repositories in case cli_exit_tools or pathlib3x is broken on pypi
    # cli_exit_tools @ git+https://github.com/bitranox/cli_exit_tools.git
    # pathlib3x @ git+https://github.com/bitranox/pathlib3x.git
    cli_exit_tools
    pathlib3x

Acknowledgements
----------------

- special thanks to "uncle bob" Robert C. Martin, especially for his books on "clean code" and "clean architecture"

Contribute
----------

I would love for you to fork and send me pull request for this project.
- `please Contribute <https://github.com/bitranox/PizzaCutter/blob/master/CONTRIBUTING.md>`_

License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

---

Changelog
=========

- new MAJOR version for incompatible API changes,
- new MINOR version for added functionality in a backwards compatible manner
- new PATCH version for backwards compatible bug fixes

v1.1.10
--------
2023-07-21:
    - require minimum python 3.8
    - remove python 3.7 tests
    - introduce PEP517 packaging standard
    - introduce pyproject.toml build-system
    - remove mypy.ini
    - remove pytest.ini
    - remove setup.cfg
    - remove setup.py
    - remove .bettercodehub.yml
    - remove .travis.yml
    - update black config
    - clean ./tests/test_cli.py
    - add codeql badge
    - move 3rd_party_stubs outside the src directory to ``./.3rd_party_stubs``
    - add pypy 3.10 tests
    - add python 3.12-dev tests

v1.1.9
--------
2020-10-09: service release
    - update travis build matrix for linux 3.9-dev
    - update travis build matrix (paths) for windows 3.9 / 3.10

v1.1.8
--------
2020-08-08: service release
    - fix documentation
    - fix travis
    - deprecate pycodestyle
    - implement flake8

v1.1.7
---------
2020-08-01: fix pypi deploy

v1.1.6
---------
2020-07-31: fix travis build

v0.1.5
---------
2020-07-30: release
    - add helper "find_version_number_in_file"

v0.1.4
---------
2020-07-29: release
    - use the new pizzacutter template
    - use cli_exit_tools

v0.1.3
---------
2020-07-16: release
    - change the location of the python default template

v0.1.2
---------
2020-07-16: release
    - release on pypi

v0.1.1
---------
2020-07-16: release
    - fix cli test
    - enable traceback option on cli errors

v0.1.0
---------
2020-05-24: Initial public release

