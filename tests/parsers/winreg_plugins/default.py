#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the default Windows Registry plugin."""

import unittest

from plaso.dfwinreg import definitions as dfwinreg_definitions
from plaso.formatters import winreg as _  # pylint: disable=unused-import
from plaso.lib import timelib
from plaso.parsers.winreg_plugins import default

from tests.dfwinreg import test_lib as dfwinreg_test_lib
from tests.parsers.winreg_plugins import test_lib


class TestDefaultRegistry(test_lib.RegistryPluginTestCase):
  """Tests for the default Windows Registry plugin."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._plugin = default.DefaultPlugin()

  def testProcess(self):
    """Tests the Process function."""
    key_path = u'\\Microsoft\\Some Windows\\InterestingApp\\MRU'
    values = []
    values.append(dfwinreg_test_lib.TestRegValue(
        u'MRUList', u'acb'.encode(u'utf_16_le'),
        dfwinreg_definitions.REG_SZ, offset=123))
    values.append(dfwinreg_test_lib.TestRegValue(
        u'a', u'Some random text here'.encode(u'utf_16_le'),
        dfwinreg_definitions.REG_SZ, offset=1892))
    values.append(dfwinreg_test_lib.TestRegValue(
        u'b', u'c:/evil.exe'.encode(u'utf_16_le'),
        dfwinreg_definitions.REG_BINARY, offset=612))
    values.append(dfwinreg_test_lib.TestRegValue(
        u'c', u'C:/looks_legit.exe'.encode(u'utf_16_le'),
        dfwinreg_definitions.REG_SZ, offset=1001))

    timestamp = timelib.Timestamp.CopyFromString(u'2012-08-28 09:23:49.002031')
    winreg_key = dfwinreg_test_lib.TestRegKey(key_path, timestamp, values, 1456)

    event_queue_consumer = self._ParseKeyWithPlugin(self._plugin, winreg_key)
    event_objects = self._GetEventObjectsFromQueue(event_queue_consumer)

    self.assertEqual(len(event_objects), 1)

    event_object = event_objects[0]

    # This should just be the plugin name, as we're invoking it directly,
    # and not through the parser.
    self.assertEqual(event_object.parser, self._plugin.plugin_name)

    expected_timestamp = timelib.Timestamp.CopyFromString(
        u'2012-08-28 09:23:49.002031')
    self.assertEqual(event_object.timestamp, expected_timestamp)

    expected_msg = (
        u'[{0:s}] '
        u'MRUList: [REG_SZ] acb '
        u'a: [REG_SZ] Some random text here '
        u'b: [REG_BINARY] '
        u'c: [REG_SZ] C:/looks_legit.exe').format(key_path)

    expected_msg_short = (
        u'[{0:s}] MRUList: [REG_SZ] acb a: [REG_SZ...').format(key_path)

    self._TestGetMessageStrings(event_object, expected_msg, expected_msg_short)


if __name__ == '__main__':
  unittest.main()
