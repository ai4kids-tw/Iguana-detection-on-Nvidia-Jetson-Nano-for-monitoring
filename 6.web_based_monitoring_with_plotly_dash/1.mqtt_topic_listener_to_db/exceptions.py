class MqttBrokerConfigFileNotFoundError (Exception):
    """Exception raised when no mqtt broker configure file is not found.

    Attributes:
        file_path -- mqtt broker configure file path which caused the error
        message -- explanation of the error
    """

    def __init__(self, file_path, message="MqttConfigFileNotFoundError: No such file exists."):
        self.file_path = file_path
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_path} -> {self.message}'


class DatabaseConfigFileNotFoundError(Exception):
    """Exception raised if mqtt configure file not found.

    Attributes:
        salary -- input salary which caused the error
        message -- explanation of the error
    """

    def __init__(self, file_path, message="DatabaseConfigFileNotFoundError: No such file exists."):
        self.file_path = file_path
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_path} -> {self.message}'