import subprocess

import logging
logger = logging.getLogger(__name__)


def is_rdiag_available():
    """
    Checks if r.diag utility is available and can be used in tests
    :return:
    """
    p = subprocess.Popen(["which", "r.diag"], stdout=subprocess.PIPE, stderr=None, shell=False)
    (out, err) = p.communicate()
    if out.decode().strip() == "":
        logger.warning("Could not find r.diag, this is not critical, but some tests will not be run.")
        return False
    return True