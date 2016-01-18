from __future__ import absolute_import
__author__ = 'huziy'

import os


def get_input_file_path(filename, script_dir):
    """
    Get the absolute path to the file 'filename' used for testing
    :param filename:
    """
    # Determine the path to the file, so it is accessible when installed
    in_path = os.path.join(script_dir, "data", filename)

    # Cover the case when tests are run in the dev version of the project
    if not os.path.exists(in_path):
        in_path = os.path.join("data", filename)

    return in_path
