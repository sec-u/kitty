# Copyright (C) 2016 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
#
# This file is part of Kitty.
#
# Kitty is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Kitty is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Kitty.  If not, see <http://www.gnu.org/licenses/>.


class Report(object):
    '''
    This class represent a report for a single test.
    This report may contain subreports from nested entities.

    :example:

        In this example, the report, generated by the controller, indicates
        failure.

        ::

            report = Report('Controller')
            report.add('generation time', 0)
            report.failed('target does not respont')
    '''

    def __init__(self, name, default_failed=False):
        '''
        :param name: name of the report (or the issuer)
        :param default_failed: is the default status of the report failed (default: False)
        '''
        self._data_fields = {}
        self._sub_reports = {}
        self._name = name
        self._default_failed = default_failed
        self.clear()

    def clear(self):
        '''
        Set the report to its defaults.
        This will clear the report, keeping only the name and setting the
        failure status to the default.
        '''
        self._data_fields = {}
        self._sub_reports = {}
        self.add('failed', self._default_failed)
        self.add('name', self._name)
        self.add('sub_reports', [])

    def get_name(self):
        '''
        :return: the name of the report
        '''
        return self.get('name')

    def success(self):
        '''
        Set the failure status to False.
        '''
        self.add('failed', False)
        if 'failure_reason' in self._data_fields:
            del self._data_fields['failure_reason']

    def failed(self, reason=None):
        '''
        Set the failure status to True, and set the failure reason

        :param reason: failure reason (default: None)
        '''
        self.add('failed', True)
        if reason:
            self.add('failure_reason', reason)

    def add(self, key, value):
        '''
        Add an entry to the report

        :param key: entry's key
        :param value: the actual value

        :example:

            ::

                my_report.add('retriy count', 3)
        '''
        if isinstance(value, Report):
            self._sub_reports[key] = value
            self._data_fields['sub_reports'].append(key)
        else:
            self._data_fields[key] = value

    def get(self, key):
        '''
        Get a value for a given key

        :param key: entry's key
        :return: corresponding value
        '''
        if key in self._data_fields:
            return self._data_fields[key]
        if key in self._sub_reports:
            return self._sub_reports[key]
        return None

    def to_dict(self, encoding='base64'):
        '''
        Return a dictionary version of the report

        :param encoding: required encoding for the string values (default: 'base64')
        :rtype: dictionary
        :return: dictionary representation of the report
        '''
        res = {}
        for k, v in self._data_fields.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            if type(v) == str:
                v = v.encode(encoding)[:-1]
            res[k] = v
        for k, v in self._sub_reports.items():
            res[k] = v.to_dict(encoding)
        return res

    @classmethod
    def _decode(cls, val, encoding):
        if type(val) == str:
            val = val.decode(encoding)
        return val

    @classmethod
    def from_dict(cls, d, encoding='base64'):
        '''
        Construct a ``Report`` object from dictionary.

        :type d: dictionary
        :param d: dictionary representing the report
        :param encoding: encoding of strings in the dictionary (default: 'base64')
        :return: Report object
        '''
        report = Report(Report._decode(d['name'], encoding))
        report.add('failed', Report._decode(d['failed'], encoding))
        sub_reports = Report._decode(d['sub_reports'], encoding)
        del d['sub_reports']
        for k, v in d.items():
            if k in sub_reports:
                report.add(k, Report.from_dict(v))
            else:
                report.add(k, Report._decode(v, encoding))

        return report

    def is_failed(self):
        '''
        :return: True if the report or any sub report indicates failure.
        '''
        failed = self.get('failed')
        for subreport in self._sub_reports.values():
            failed |= subreport.is_failed()
        return failed
