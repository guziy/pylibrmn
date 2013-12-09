from nose.tools import ok_
from rpn.rpn import RPN
import numpy as np
__author__ = 'huziy'


class TestRpn(RPN):
    def __init__(self):
        """
        Note a new object TestRpn is created for each test
        """
        path = "data/test.rpn"
        RPN.__init__(self, path=path)
        self.defaultVarName = "I5"

    def test_dateo(self):
        """
         Test dateo calculation
        """
        field = self.get_first_record_for_name(self.defaultVarName)
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
        field = self.get_first_record_for_name(self.defaultVarName)
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
        ok_("I5" in the_names)
        ok_(">>" in the_names)
        ok_("^^" in the_names)

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
        self.get_first_record_for_name(self.defaultVarName)
        info = self.get_proj_parameters_for_the_last_read_rec()
        ok_(info["grid_type"] == "E", msg="Expected {0} but got {1} instead".format("E", info["grid_type"]))


    def test_get_4d_field(self):
        """
            Test getting a 4d field in time and space
        """
        data = self.get_4d_field(self.defaultVarName)
        ntimes = len(data)
        print data, len(data), ntimes
        nlevs = len(data.items()[0][1])
        msg = "The test file should contain {2} on 1 level at 1 timestep, not nlevs={0} and ntimes={1}"
        ok_(ntimes == 1 and nlevs == 1,
            msg= msg.format(nlevs, ntimes, self.defaultVarName))

    def teardown(self):
        """
            Called after each test
        """
        self.close()


def test_get_records_for_foreacst_hour():
    path = "data/test.rpn"

    rObj = RPN(path)
    nRecords = rObj.get_number_of_records()

    print nRecords

    res = rObj.get_records_for_foreacst_hour(var_name="I5", forecast_hour=108072)
    ok_(len(res) == 1, msg="SWE has only one vertical level ..., not {0} ".format(len(res)))

    res = rObj.get_records_for_foreacst_hour(var_name="I5", forecast_hour=10)
    ok_(len(res) == 0)
    ok_(nRecords == 3, msg="The number of records is not what I've expected ")

    #assert_(len(res) == 1, msg="Only one record in the file for the forecast_hour = 0")

    rObj.close()


def test_polar_stereographic():
    """
    Testing polar stereographic grid functions
    """
    path = "data/mappe.rpnw"
    r = RPN(path)
    mk = r.get_first_record_for_name("MK")

    #print r.get_proj_parameters_for_the_last_read_rec()
    lons, lats = r.get_longitudes_and_latitudes_for_the_last_read_rec()
    amno_link = "http://www.cccma.ec.gc.ca/data/grids/geom_crcm_amno_182x174.shtml"
    msg_tpl = "Geenrated longitudes are not the same as {0}".format(amno_link)
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





def teardown():
    print "tearing down the test suite"

if __name__ == "__main__":
    theTest = TestRpn()

