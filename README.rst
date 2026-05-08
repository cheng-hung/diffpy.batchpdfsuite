|Icon| |title|_
===============

.. |title| replace:: diffpy.batchpdfsuite
.. _title: https://diffpy.github.io/diffpy.batchpdfsuite

.. |Icon| image:: https://avatars.githubusercontent.com/diffpy
        :target: https://diffpy.github.io/diffpy.batchpdfsuite
        :height: 100px

|PyPI| |Forge| |PythonVersion| |PR|

|CI| |Codecov| |Black| |Tracking|

.. |Black| image:: https://img.shields.io/badge/code_style-black-black
        :target: https://github.com/psf/black

.. |CI| image:: https://github.com/diffpy/diffpy.batchpdfsuite/actions/workflows/matrix-and-codecov-on-merge-to-main.yml/badge.svg
        :target: https://github.com/diffpy/diffpy.batchpdfsuite/actions/workflows/matrix-and-codecov-on-merge-to-main.yml

.. |Codecov| image:: https://codecov.io/gh/diffpy/diffpy.batchpdfsuite/branch/main/graph/badge.svg
        :target: https://codecov.io/gh/diffpy/diffpy.batchpdfsuite

.. |Forge| image:: https://img.shields.io/conda/vn/conda-forge/diffpy.batchpdfsuite
        :target: https://anaconda.org/conda-forge/diffpy.batchpdfsuite

.. |PR| image:: https://img.shields.io/badge/PR-Welcome-29ab47ff
        :target: https://github.com/diffpy/diffpy.batchpdfsuite/pulls

.. |PyPI| image:: https://img.shields.io/pypi/v/diffpy.batchpdfsuite
        :target: https://pypi.org/project/diffpy.batchpdfsuite/

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/diffpy.batchpdfsuite
        :target: https://pypi.org/project/diffpy.batchpdfsuite/

.. |Tracking| image:: https://img.shields.io/badge/issue_tracking-github-blue
        :target: https://github.com/diffpy/diffpy.batchpdfsuite/issues

GUI for batch refinements of multiple PDF datasets

* LONGER DESCRIPTION HERE

For more information about the diffpy.batchpdfsuite library, please consult our `online documentation <https://diffpy.github.io/diffpy.batchpdfsuite>`_.

Citation
--------

If you use diffpy.batchpdfsuite in a scientific publication, we would like you to cite this package as

        diffpy.batchpdfsuite Package, https://github.com/diffpy/diffpy.batchpdfsuite

Installation
------------

The preferred method is to use `Miniconda Python
<https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html>`_
and install from the "conda-forge" channel of Conda packages.

To add "conda-forge" to the conda channels, run the following in a terminal. ::

        conda config --add channels conda-forge

We want to install our packages in a suitable conda environment.
The following creates and activates a new environment named ``diffpy.batchpdfsuite_env`` ::

        conda create -n diffpy.batchpdfsuite_env diffpy.batchpdfsuite
        conda activate diffpy.batchpdfsuite_env

The output should print the latest version displayed on the badges above.

If the above does not work, you can use ``pip`` to download and install the latest release from
`Python Package Index <https://pypi.python.org>`_.
To install using ``pip`` into your ``diffpy.batchpdfsuite_env`` environment, type ::

        pip install diffpy.batchpdfsuite

If you prefer to install from sources, after installing the dependencies, obtain the source archive from
`GitHub <https://github.com/diffpy/diffpy.batchpdfsuite/>`_. Once installed, ``cd`` into your ``diffpy.batchpdfsuite`` directory
and run the following ::

        pip install .

This package also provides command-line utilities. To check the software has been installed correctly, type ::

        diffpy.batchpdfsuite --version

You can also type the following command to verify the installation. ::

        python -c "import diffpy.batchpdfsuite; print(diffpy.batchpdfsuite.__version__)"


To view the basic usage and available commands, type ::

        diffpy.batchpdfsuite -h

Getting Started
---------------

You may consult our `online documentation <https://diffpy.github.io/diffpy.batchpdfsuite>`_ for tutorials and API references.

Support and Contribute
----------------------

If you see a bug or want to request a feature, please `report it as an issue <https://github.com/diffpy/diffpy.batchpdfsuite/issues>`_ and/or `submit a fix as a PR <https://github.com/diffpy/diffpy.batchpdfsuite/pulls>`_.

Feel free to fork the project and contribute. To install diffpy.batchpdfsuite
in a development mode, with its sources being directly used by Python
rather than copied to a package directory, use the following in the root
directory ::

        pip install -e .

To ensure code quality and to prevent accidental commits into the default branch, please set up the use of our pre-commit
hooks.

1. Install pre-commit in your working environment by running ``conda install pre-commit``.

2. Initialize pre-commit (one time only) ``pre-commit install``.

Thereafter your code will be linted by black and isort and checked against flake8 before you can commit.
If it fails by black or isort, just rerun and it should pass (black and isort will modify the files so should
pass after they are modified). If the flake8 test fails please see the error messages and fix them manually before
trying to commit again.

Improvements and fixes are always appreciated.

Before contributing, please read our `Code of Conduct <https://github.com/diffpy/diffpy.batchpdfsuite/blob/main/CODE-OF-CONDUCT.rst>`_.

Contact
-------

For more information on diffpy.batchpdfsuite please visit the project `web-page <https://diffpy.github.io/>`_ or email the maintainers ``Yuchen Xiao(yx2924@columbia.edu) and Simon Billinge(sbillinge@ucsb.edu)``.

Acknowledgements
----------------

``diffpy.batchpdfsuite`` is built and maintained with `scikit-package <https://scikit-package.github.io/scikit-package/>`_.
