#!/usr/bin/python

# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from __future__ import absolute_import, division, print_function


class FilterModule(object):
  def filters(self):
    return {
        'filter_01': self.filter_01,
        'filter_02': self.filter_02,
    }

  def filter_01(self, value):
    return 'org2-collection3-filter1' + ' -> ' + str(value)

  def filter_02(self, value):
    return 'org2-collection3-filter2' + ' -> ' + str(value)
