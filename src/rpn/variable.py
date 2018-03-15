from __future__ import absolute_import
import numpy as np


class RPNVariable(object):

    def __init__(self, rpn_obj, name):
        self.rpn_obj = rpn_obj
        self.name = name


        self.sorted_levels = []
        self.sorted_dates = []


        # {datetime: {level: rpn_file_internal key}}
        self.data_hints = {}
        self.__init_data_hints()


        #  data type
        self.dtype = np.float

        self._shape = None


    def __init_data_hints(self):
        # assert isinstance(self.rpn_obj, RPN)
        self.data_hints = self.rpn_obj.get_date_level_key_mapping_for_name(varname=self.name)

        for d, lev_to_key in self.data_hints.items():
            self.sorted_dates.append(d)

            if len(self.sorted_levels) == 0:
                self.sorted_levels = np.array(sorted([lev for lev in lev_to_key]))

        # sort the dates
        self.sorted_dates = sorted(self.sorted_dates)


    @property
    def shape(self):
        if self._shape is None:
            # assert isinstance(self.rpn_obj, RPN)
            nt = len(self.data_hints)

            z_to_field = next(iter(self.data_hints.items()))[1]
            nz = len(z_to_field)

            nx, ny = self.rpn_obj.get_field_shape(varname=self.name)


            self._shape = (nt, nz, nx, ny)

        return self._shape


    def __getitem__(self, slices):
        """
        first dimension is time
        second - vertical levels (sorted according to the value, so in the case of pressure the highest level will have index 0)
        third - longitudes
        fourth - latitudes

        Note: you might want to use squeeze for 2D arrays, because even for the surface pressure for example you would get
        (Nt, 1, Nx, Ny), i.e. 1 - vertical level

        :param slices:
        :return:
        """
        # from rpn.rpn import RPN
        # assert isinstance(self.rpn_obj, RPN)

        data = []
        slice_t = slices[0] if isinstance(slices, tuple) else slices
        slice_z = slices[1] if isinstance(slices, tuple) and len(slices) > 1 else slice(None)
        slice_x = slices[2] if isinstance(slices, tuple) and len(slices) > 2 else slice(None)
        slice_y = slices[3] if isinstance(slices, tuple) and len(slices) > 3 else slice(None)

        times = self.sorted_dates[slice_t]
        levels = self.sorted_levels[slice_z]


        try:
            _ = (t for t in times)
        except TypeError:
            times = [times]

        try:
            _ = (l for l in levels)
        except TypeError:
            levels = [levels]


        for ti, t in enumerate(times):
            data.append([])
            for levi, lev in enumerate(levels):

                data_chunk = self.rpn_obj._get_data_by_key(self.data_hints[t][lev])[slice_x, slice_y, :]
                if data_chunk.ndim == 3 and data_chunk.shape[-1] == 1:
                    data_chunk = data_chunk.squeeze(axis=2)

                data[ti].append(data_chunk)

        data = np.array(data)

        return data




