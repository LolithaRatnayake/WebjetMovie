# Thse custom classes are used to mark / handle errors


class ServerSideError(Exception):
    """
    This exception is used to mark Serverside errors which will give masked output as error
    """
    def __init__(self, title: str, detail: str = None):
        self.log_error_string = 'Error {} has occured: {}'.format(title, detail)
        super().__init__(self.log_error_string)


class ClientSideError(Exception):
    """
    This exception is used to mark client side errors.
    """
    def __init__(self, title: str = None, detail: str = None):
        self.log_error_string = 'Error {} has occured: {}'.format(title, detail)
        super().__init__(self.log_error_string)
