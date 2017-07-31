from __future__ import absolute_import
from nose.tools import ok_
from nose import tools
import subprocess
from rpn.rpn import RPN
import numpy as np

from rpn.util.bash_utils import is_rdiag_available

__author__ = 'huziy'

from rpn.tests.utils import get_input_file_path
import os

the_dir, script_name = os.path.split(__file__)
in_path = get_input_file_path("test.rpn", the_dir)


def test_write_field_2d_clean():
    """
    Testing write 2d field

    """
    import os
    tfile = "temp.rpn"
    r = None
    try:
        r = RPN(tfile, mode="w")
        data = np.random.randn(10, 10)
        data = data.astype(np.float32)
        r.write_2d_field_clean(data, properties={"name": "RAND"})
        r.close()

        r = RPN(tfile)
        data1 = r.get_first_record_for_name("RAND")
        v0, v1 = data.mean(), data1.mean()

        ok_(abs(v1 - v0) <= 1e-6, "Saved ({0}) and retrieved ({1}) means are not the same.".format(v0, v1))

    finally:
        if r is not None:
            r.close()

        os.remove(tfile)


def test_write_field_2d_64bits():
    """
    Test writing a 64 bit precision
    """
    import os
    tfile = "temp.rpn"
    r = None
    try:
        r = RPN(tfile, mode="w")
        data = np.random.randn(10, 10)
        data = data.astype(np.float64)
        r.write_2d_field_clean(data, properties={"name": "RAND", "nbits": -64})
        r.close()

        r = RPN(tfile)
        data1 = r.get_first_record_for_name("RAND")
        v0, v1 = data.mean(), data1.mean()

        ok_(abs(v1 - v0) <= 1e-15, "Saved ({0}) and retrieved ({1}) means are not the same.".format(v0, v1))

    finally:
        r.close()
        os.remove(tfile)


class TestRpn(RPN):
    def __init__(self):
        """
        Note a new object TestRpn is created for each test
        """
        path = in_path
        super(self.__class__, self).__init__(path=path)
        self.default_var_name = "I5"


    def test_set_file_unit_should_fail(self):
        tools.assert_raises(Exception, self.file_unit, 10)


    def test_get_longitudes_and_latitudes_of_the_last_read_record(self):
        """
        Test get_longitudes_and_latitudes_for_the_last_read_rec
        """
        data = []
        nrecords_read = 0
        while data is not None:
            data = self.get_next_record()
            if data is None:
                break
            nrecords_read += 1
            print(self.get_current_info())


        ok_(nrecords_read >= 1, msg="At least one record should have been read")
        ok_(nrecords_read == self.get_number_of_records(), "Should have read all {} records, but got only {}".format(self.get_number_of_records(), nrecords_read))

        # there is only I5 and >>, ^^ in the file, which won't mess the current_info dictionary
        if self.get_current_info()["varname"] == self.default_var_name:
            _, _ = self.get_longitudes_and_latitudes_for_the_last_read_rec()


    def test_compare_with_ggstat(self):
        if not is_rdiag_available():
            print("Warning: disabling comparison tests with r.diag, since r.diag is not installed")
            return
        data = self.get_first_record_for_name(self.default_var_name)
        proc = subprocess.Popen(["r.diag", "ggstat", self.path], stdout=subprocess.PIPE)
        (out, err) = proc.communicate()

        lines = out.decode().split("\n")
        lines = list(filter(lambda line: ("I5" in line), lines))

        fields = lines[0].split()

        the_mean = float(fields[12])
        the_variance = float(fields[13])
        msg = "The mean does not correspond to ggstat: {0} <> {1}".format(data.mean(), the_mean)
        ok_(abs(data.mean() - the_mean) < 1e-3, msg=msg)

        msg = "The variance does not correspond to ggstat: {0} <> {1}".format(data.var(), the_variance)
        ok_(abs(data.var() - the_variance) < 1e-1, msg=msg)


    def test_dateo(self):
        """
         Test dateo calculation
        """
        field = self.get_first_record_for_name(self.default_var_name)
        print(self.get_dateo_of_last_read_record())
        #print(self._dateo_to_string(-1274695862))

        expect = "1979-01-01 00:00:00"
        got = self.get_dateo_of_last_read_record().strftime("%Y-%m-%d %H:%M:%S")

        ok_(expect == got,
            msg="Date of origin is not what is expected.\nExpected: {0}\nGot: {1}".format(expect, got))

    def test_date(self):
        """
         Test valid date calculation
        """
        field = self.get_first_record_for_name(self.default_var_name)
        print(self.get_dateo_of_last_read_record())
        #print(self._dateo_to_string(-1274695862))

        expect = "1991-05-01 00:00:00"
        got = self.get_datetime_for_the_last_read_record().strftime("%Y-%m-%d %H:%M:%S")
        ok_(expect == got,
            msg="Date of origin is not what is expected.\nExpected: {0}\nGot: {1}".format(expect, got))

    def test_get_varnames(self):
        """
            Test if the var names are retrieved correctly
        """
        the_names = self.get_list_of_varnames()
        # I know that the current test file should contain the following
        ok_("I5" in the_names, "Expected to find I5 variable in {}".format(self.path))
        ok_(">>" in the_names, "Expected to find >> variable in {}".format(self.path))
        ok_("^^" in the_names, "Expected to find ^^ variable in {}".format(self.path))


    def test_get_tictacs_not_fails(self):
        i5 = self.get_first_record_for_name("I5")
        rlon, rlat = self.get_tictacs_for_the_last_read_record()
        lons, lats = self.get_longitudes_and_latitudes_for_the_last_read_rec()

        ok_(lons.shape == (rlon.shape[0], rlat.shape[0]), "Expected len(rlon)={} and len(rlat)={}, but got len(rlon)={} and len(rlat)={}".format(lons.shape[0], lons.shape[1], len(rlon), len(rlat)))


    def test_get_grid_parameters_for_the_last_read_rec(self):
        """
        Test if the coordinates of the two equator points are identified correctly from the file
        metadata accuracy required is +/- 1.0e-5
        """
        self.get_first_record_for_name("I5")
        params = self.get_proj_parameters_for_the_last_read_rec()

        #these are taken from gemclim_settings.nml
        lat1 = 52.0
        lon1 = -68.0 + 360
        lat2 = 0.0
        lon2 = 16.65

        err_max = 1.0e-5

        err1 = np.abs(lat1 - params["lat1"])
        err2 = np.abs(lon1 - params["lon1"])
        err3 = np.abs(lat2 - params["lat2"])
        err4 = np.abs(lon2 - params["lon2"])

        ok_(err1 < err_max, msg="the lat1 accuracy is not very good: {0}".format(err1))
        ok_(err2 < err_max, msg="the lon1 accuracy is not very good: {0}".format(err2))
        ok_(err3 < err_max, msg="the lat2 accuracy is not very good: {0}".format(err3))
        ok_(err4 < err_max, msg="the lon2 accuracy is not very good: {0}".format(err4))

    def test_if_grid_type_is_correct(self):
        """
            Test grid type extraction
        """
        self.get_first_record_for_name(self.default_var_name)
        info = self.get_proj_parameters_for_the_last_read_rec()
        ok_(info["grid_type"] == "E",
            msg="Expected {0} but got {1} instead".format("E".encode(), info["grid_type"]))

    def test_get_4d_field(self):
        """
            Test getting a 4d field in time and space
        """
        data = self.get_4d_field(self.default_var_name)
        ntimes = len(data)
        print(data, len(data), ntimes)
        nlevs = len([v for k, v in data.items()][0])
        msg = "The test file should contain {2} on 1 level at 1 timestep, not nlevs={0} and ntimes={1}"
        ok_(ntimes == 1 and nlevs == 1,
            msg=msg.format(nlevs, ntimes, self.default_var_name))

    def test_ip1_level_kind(self):
        """
        Test conversion from ip1 to the real value of a vertical level
        :return:
        """

        def __test_ip1_to_level(ip1=72712562, expect_lev=36081.8, tolerance=0.1):
            calc_lev = self.ip1_to_real_val(ip1=ip1)
            msg = "Expect {} for ip1={}, but got {}".format(expect_lev, ip1, calc_lev)
            ok_(np.abs(calc_lev - expect_lev) < tolerance, msg=msg)

        __test_ip1_to_level()
        __test_ip1_to_level(ip1=93423264, expect_lev=1)  # hydrid
        __test_ip1_to_level(ip1=0, expect_lev=0)  # surface
        __test_ip1_to_level(ip1=975, expect_lev=975, tolerance=1.0e-6)  # pressure
        __test_ip1_to_level(ip1=60068832, expect_lev=3, tolerance=1.0e-6)  # arbitrary

    def teardown(self):
        """
            Called after each test
        """
        self.close()


def test_get_records_for_foreacst_hour():
    r_obj = None
    try:
        r_obj = RPN(in_path)
        n_records = r_obj.get_number_of_records()

        print(n_records)

        res = r_obj.get_records_for_foreacst_hour(var_name="I5", forecast_hour=108072)
        ok_(len(res) == 1, msg="SWE has only one vertical level ..., not {0} ".format(len(res)))

        res = r_obj.get_records_for_foreacst_hour(var_name="I5", forecast_hour=10)
        ok_(len(res) == 0)
        ok_(n_records == 3, msg="The number of records is not what I've expected ")

        #assert_(len(res) == 1, msg="Only one record in the file for the forecast_hour = 0")
    
    finally:
        if r_obj is not None:
            r_obj.close()


def test_polar_stereographic():
    """
    Testing polar stereographic grid functions
    """
    path = get_input_file_path("mappe.rpnw", the_dir)
    r = None
    try:
        r = RPN(path)
        mk = r.get_first_record_for_name("MK")

        #print r.get_proj_parameters_for_the_last_read_rec()
        lons, lats = r.get_longitudes_and_latitudes_for_the_last_read_rec()
        amno_link = "http://www.cccma.ec.gc.ca/data/grids/geom_crcm_amno_182x174.shtml"
        msg_tpl = "Generated longitudes are not the same as {0}".format(amno_link)
        msg_tpl += "\n Expected: {0}"
        msg_tpl += "\n Got: {1}"

        #test with expected values from the EC website
        expect = 226.50 - 360.0
        msg = msg_tpl.format(expect, lons[10, 10])
        ok_(np.abs(lons[10, 10] - expect) < 1.0e-2, msg=msg)

        #latitudes
        expect = 41.25
        msg = msg_tpl.format(expect, lats[-11, -11])
        ok_(np.abs(lats[-11, -11] - expect) < 1.0e-2, msg=msg)

    finally:
        if r is not None:
            r.close()


def teardown():
    print("tearing down the test suite")




if __name__ == "__main__":
    theTest = TestRpn()
