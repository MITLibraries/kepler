# -*- coding: utf-8 -*-
from __future__ import absolute_import
import decimal
import arrow
from kepler.exceptions import InvalidDataError


class RecordMeta(type):
    def __new__(cls, clsname, bases, methods):
        for k, v in methods.items():
            if isinstance(v, Descriptor):
                v.name = k
        return type.__new__(cls, clsname, bases, methods)


class Descriptor(object):
    def __init__(self, name=None, **opts):
        self.name = name
        for k, v in opts.items():
            setattr(self, k, v)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class Default(Descriptor):
    def __get__(self, instance, owner):
        try:
            return instance.__dict__.get(self.name, self.default)
        except AttributeError:
            return instance.__dict__.get(self.name)


class Enum(Default):
    def __set__(self, instance, value):
        if value in self.enums:
            super(Enum, self).__set__(instance, value)
        else:
            raise InvalidDataError(self.name, value)


class String(Default):
    def __init__(self, name=None, **opts):
        defaults = {'strip_ws': True}
        defaults.update(opts)
        super(String, self).__init__(name, **defaults)

    def __set__(self, instance, value):
        if self.strip_ws: value = value.strip()
        super(String, self).__set__(instance, value)


class Decimal(Default):
    def __set__(self, instance, value):
        super(Decimal, self).__set__(instance, decimal.Decimal(value))


class DateTime(Descriptor):
    def __set__(self, instance, value):
        super(DateTime, self).__set__(instance, arrow.get(value))

    def __get__(self, instance, owner):
        try:
            return instance.__dict__.get(self.name, arrow.get(self.default))
        except AttributeError:
            return instance.__dict__.get(self.name)


class Integer(Default):
    def __set__(self, instance, value):
        super(Integer, self).__set__(instance, int(value))


class Set(Descriptor):
    def __set__(self, instance, value):
        super(Set, self).__set__(instance, set(value))

    def __get__(self, instance, owner):
        if instance.__dict__.get(self.name) is None:
            self.__set__(instance, set())
        return instance.__dict__.get(self.name)


class Dictionary(Descriptor):
    def __get__(self, instance, owner):
        if instance.__dict__.get(self.name) is None:
            self.__set__(instance, dict())
        return instance.__dict__.get(self.name)
