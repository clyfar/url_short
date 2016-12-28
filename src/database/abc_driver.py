#!/usr/bin/env python
# Author: Geoffrey Golliher (ggolliher@katch.com)

from abc import ABCMeta, abstractmethod

class AbstractDBDriver(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def connect_db(self):
        raise NotImplemented

    @abstractmethod
    def init_db(self):
        raise NotImplemented

    @abstractmethod    
    def last_id(self):
        raise NotImplemented

    @abstractmethod    
    def transform_shorties(self):
        raise NotImplemented
