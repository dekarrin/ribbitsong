import unittest
from unittest.mock import patch

from frogcherub import forms, util

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
        give_default = util.SequenceProvider("one", "two", "three")
    
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
    
    @patch('builtins.input', side_effect=["answer"])
    def test_entry_hook_normal_field(self, _):
        received = None
        def hook(v):
            nonlocal received
            received = v
        
        self.sut.add_field("test", entry_hook=hook)
        
        self.sut.fill()
        
        actual = received
        expected = "answer"
        
        self.assertEqual(actual, expected)
    
    def test_entry_hook_auto_uuid_field(self):
        received = None
        def hook(v):
            nonlocal received
            received = v
        
        self.sut.add_auto_uuid_field("test", entry_hook=hook)
        
        self.sut.fill()
        
        self.assertIsNotNone(received)
    
    @patch('builtins.input', side_effect=["answer1", "answer2"])
    def test_done_hook(self, _):
        called = True
        def hook(*args):
            nonlocal called
            called = True
        
        subform = self.sut.add_object_field("test", done_hook=hook)
        subform.add_field("test1")
        subform.add_field("test2")
        
        self.sut.fill()
        
        self.assertTrue(called)
    
    @patch('builtins.input', side_effect=["yes", "answer1", "answer2", "yes", "answer3", "answer4", "no"])
    def test_done_hook_multivalue(self, _):
        call_count = 0
        def hook(*args):
            nonlocal call_count
            call_count += 1
        
        subform = self.sut.add_object_field("test", done_hook=hook, multivalue=True)
        subform.add_field("test1")
        subform.add_field("test2")
        
        self.sut.fill()
        
        expected = 2
        actual = call_count
        self.assertEqual(actual, expected)
    
    @patch('builtins.input', side_effect=["yes", "answer1", "answer2"])
    def test_done_hook_nullable_nonnull(self, _):
        call_count = 0
        def hook(*args):
            nonlocal call_count
            call_count += 1
        
        subform = self.sut.add_object_field("test", done_hook=hook, nullable=True)
        subform.add_field("test1")
        subform.add_field("test2")
        
        self.sut.fill()
        
        expected = 1
        actual = call_count
        self.assertEqual(actual, expected)
    
    @patch('builtins.input', side_effect=["no"])
    def test_done_hook_nullable_null(self, _):
        call_count = 0
        def hook(*args):
            nonlocal call_count
            call_count += 1
        
        subform = self.sut.add_object_field("test", done_hook=hook, nullable=True)
        subform.add_field("test1")
        subform.add_field("test2")
        
        self.sut.fill()
        
        expected = 1
        actual = call_count
        self.assertEqual(actual, expected)
    
    @patch('builtins.input', side_effect=["yes", "yes", "answer1", "answer2", "yes", "no", "no"])
    def test_done_hook_multivalue_nullable(self, _):
        call_count = 0
        def hook(*args):
            nonlocal call_count
            call_count += 1
        
        subform = self.sut.add_object_field("test", done_hook=hook, nullable=True, multivalue=True)
        subform.add_field("test1")
        subform.add_field("test2")
        
        result = self.sut.fill()
        
        expected = 2
        actual = call_count
        self.assertEqual(actual, expected)
        
        
        
        
        
        
