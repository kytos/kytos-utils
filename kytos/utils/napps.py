from kytos.utils.exceptions import KytosException

class NappsManager:
    @staticmethod
    def create(null=None):
        # TODO: Remove the null args
        print("Creating a NApp struct")

    @staticmethod
    def enable(napps):
        if not napps:
            raise KytosException("Missing argument")

        print("Enabling napps {}".format(napps))

    @staticmethod
    def disable(napps):
        if not napps:
            raise KytosException("Missing argument")

        print("Disabling napps {}".format(napps))

    @staticmethod
    def list(null=None):

        # TODO: Remove the null args
        print("List napp")

    @staticmethod
    def install(napps):
        if not napps:
            raise KytosException("Missing argument")

        print("Installing napps {}".format(napps))

    @staticmethod
    def uninstall(napps):
        if not napps:
            raise KytosException("Missing argument")

        print("Uninstalling napps {}".format(napps))

    @staticmethod
    def search(napp):
        print("Searching for napp {}".format(napp))
