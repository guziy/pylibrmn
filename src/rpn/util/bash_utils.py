import subprocess


def is_rdiag_available():
    """
    Checks if r.diag utility is available and can be used in tests
    :return:
    """
    p = subprocess.Popen(["which", "r.diag"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    if out.strip() == "":
        return False
    return True