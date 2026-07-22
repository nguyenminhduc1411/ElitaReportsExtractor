from abc import ABC, abstractmethod


class BaseTemplate(ABC):

    NAME = ""
    PROCEDURE = ""
    
    @abstractmethod
    def match(self, text):
        pass

    @abstractmethod
    def parse(self, text, config):
        pass