class SpecificationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SerialisationError(Exception):
    def __init__(self, message):
        super().__init__(message)
