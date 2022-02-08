import unittest
from unittest.mock import patch

from ribbitsong import forms

class TestFormUsage(unittest.TestCase):

    @patch('builtins.input', lambda *args: 'a value')
    def test_fill_string(self):
        expected = {'test': "a value"}
        sut = forms.Form()
        sut.add_field("test")

        actual = sut.fill()

        self.assertEqual(actual, expected)
