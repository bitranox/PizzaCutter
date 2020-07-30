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

.. include:: ../pizzacutter/sub/helpers.py
    :code: python
    :start-after: # find_version_number_in_file{{{
    :end-before: # find_version_number_in_file}}}

