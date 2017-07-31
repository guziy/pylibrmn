
import numpy as np

class RPNVariable(object):

    def __init__(self, rpn_obj, name):
        self.rpn_obj = rpn_obj
        self.name = name

        # {datetime: {level: rpn_file_internal key}}
        self.data_hints = {}

        # data type
        self.dtype = np.float





    def __getitem__(self, slices):

        if not isinstance(slices, tuple):
            raise ValueError("The RPNVariable should be at least 2D")



        return None




