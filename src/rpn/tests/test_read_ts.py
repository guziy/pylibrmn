__author__ = 'huziy'


from rpn.rpn import RPN

def test_read_ts_file():
    """
    Test if the module is capable of reading the files containing timeseries data

    """

    path = "data/erai_1980-2009_PR_ts.88"

    r = RPN(path)
    pr = r.get_first_record_for_name("PR")
    print pr.shape, pr.min(), pr.max(), pr.mean(), pr.std()

    r.close()






if __name__ == "__main__":
    test_read_ts_file()