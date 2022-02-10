import unittest
from unittest.mock import patch

from frogcherub import forms

# It Would Be Nice If This Did Not Print During Every Test.
# So We Will Turn Them Off Here
@patch('builtins.print', lambda *args: None)
class TestFormUsage(unittest.TestCase):

    def setUp(self):
        self.sut = forms.Form()

    @patch('builtins.input', lambda *args: 'a value')
    def test_fill_string(self):
        expected = {'test': "a value"}
        self.sut.add_field("test")

        actual = self.sut.fill()

        self.assertEqual(actual, expected)

    @patch('builtins.input', side_effect=["value one", ""])
    def test_default_last(self, _):
        self.sut.add_field("test", default_last=True)

        actual_1 = self.sut.fill()
        actual_2 = self.sut.fill()

        # both should be the same because second should default to last entered
        expected = [
            {'test': 'value one'},
            {'test': 'value one'}
        ]
        actual = [actual_1, actual_2]

        self.assertEqual(actual, expected)
        
    @patch('builtins.input', side_effect=["", "", ""])
    def test_callable_default(self, _):
        def give_default():
            values = ["one", "two", "three"]
            for v in values:
                yield v
    
        self.sut.add_field("test", default=give_default)
        
        actual_1 = self.sut.fill()
        actual_2 = self.sut.fill()
        actual_3 = self.sut.fill()
        
        expected = [
            {'test': 'one'},
            {'test': 'two'},
            {'test': 'three'}
        ]
        actual = [actual_1, actual_2, actual_3]
        
        self.assertEqual(actual, expected)
        
        
        
        
        
