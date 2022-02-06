import atexit

from abc import ABCMeta, abstractmethod


class Exporter(metaclass=ABCMeta):
    @abstractmethod
    def export(self, value):
        pass


class TransformFileExporter(Exporter):
    def __init__(self, transform, filename):
        self.export_file = open(filename, 'w')
        self.transform = transform
        atexit.register(self._cleanup)
    
    def _cleanup(self):
        self.export_file.close()

    def export(self, tweet):
        value = tweet.transforms[self.transform]
        self.export_file.write(f"{value}\n")
        self.export_file.flush()
        