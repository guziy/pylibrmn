import glob
import os
from rpn.rpn import RPN


class MultiRPN(RPN):
    def get_output_step_in_seconds(self):
        super().get_output_step_in_seconds()

    def __init__(self, path=""):
        """
        Used to open multiple rpn  files for reading
        :param path: unix regular expression for the multiple paths
                ~ is expanded as well as environment variables ...
        """

        p1 = os.path.expanduser(path)  # expand the user if required '~'
        p2 = os.path.expandvars(p1)  # expand env vars if required

        self.path_list = glob.glob(p2)

        if len(self.path_list) == 0:
            raise FileNotFoundError("No files found for {}".format(p2))

        for p in self.path_list:
            if not os.path.isfile(p):
                raise FileNotFoundError("File {} not found".format(p))

        super().__init__(self.path_list[0])
        self.main_file = self

        self.other_files = [RPN(p) for p in self.path_list[1:]]

        self.link(self.other_files)

    def close(self):
        # unlink all the files
        self.unlink()

        # close unused files
        for f in self.other_files:
            f.close()

        super().close()


if __name__ == '__main__':
    mf = MultiRPN(path=os.path.expanduser("/home/${USER}/*.py"))
    print(mf.path_list)
