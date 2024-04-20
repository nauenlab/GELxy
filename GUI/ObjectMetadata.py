  

class ObjectMetadata:
    def __init__(self, shape, **kwargs):
        self.shape = shape
        for key, value in kwargs.items():
            setattr(self, key, value)