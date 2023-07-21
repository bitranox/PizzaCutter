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
