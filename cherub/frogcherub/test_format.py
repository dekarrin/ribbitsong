import unittest
from collections import namedtuple

from frogcherub import format


# It Would Be Nice If This Did Not Print During Every Test.
# So We Will Turn Them Off Here
class TestFormat(unittest.TestCase):
    def test_wrap_basicUsage(self):
        TC = namedtuple('TC', ['name', 'input', 'width', 'expected'])

        test_cases = [
            TC(
                name="empty input",
                input="",
                width=80,
                expected=""
            ),
            TC(
                name="not enough to wrap",
                input="a test string",
                width=80,
                expected="a test string"
            ),
            TC(
                name="2 line wrap",
                input="a string long enough to be wrapped",
                width=20,
                expected=(
                    "a string long enough\n"
                    "to be wrapped"
                )
            ),
            TC(
                name="multi-line wrap",
                input="a string long enough to be wrapped more than once",
                width=20,
                expected=(
                    "a string long enough\n"
                    "to be wrapped more\n"
                    "than once"
                )
            ),
            TC(
                name="minimum width",
                input="test",
                width=2,
                expected=(
                    "t-\n"
                    "e-\n"
                    "st"
                )
            ),
            TC(
                name="minimum width + 1",
                input="test",
                width=3,
                expected=(
                    "te-\n"
                    "st"
                )
            ),
            TC(
                name="preserve pre-existing linebreaks",
                input=(
                    "a line that will be wrapped.\n"
                    "A second line, that also will be wrapped."
                ),
                width=18,
                expected=(
                    "a line that will\n"
                    "be wrapped.\n"
                    "A second line,\n"
                    "that also will be\n"
                    "wrapped."
                )
            )
        ]

        for tc in test_cases:
            with self.subTest(tc.name, input=tc.input, width=tc.width):
                expected = tc.expected
                actual = format.wrap(tc.input, tc.width, extend=False)

                self.assertEqual(actual, expected)

    def test_wrap_extend(self):
        TC = namedtuple('TC', ['name', 'input', 'width', 'expected'])

        test_cases = [
            TC(
                name="zero-width input is extended",
                input="",
                width=4,
                expected="    "
            ),
            TC(
                name="non-wrapped line is extended",
                input="a test string",
                width=15,
                expected="a test string  "
            ),
            TC(
                name="2 line wrap is extended",
                input="a string long enough to be wrapped",
                width=20,
                expected=(
                    "a string long enough\n"
                    "to be wrapped       "
                )
            ),
            TC(
                name="multi-line wrap is extended",
                input="a string long enough to be wrapped more than once",
                width=21,
                expected=(
                    "a string long enough \n"
                    "to be wrapped more   \n"
                    "than once            "
                )
            ),
            TC(
                name="minimum width is extended",
                input="a test",
                width=2,
                expected=(
                    "a \n"
                    "t-\n"
                    "e-\n"
                    "st"
                )
            ),
            TC(
                name="minimum width + 1 is extended",
                input="a test",
                width=3,
                expected=(
                    "a  \n"
                    "te-\n"
                    "st "
                )
            ),
            TC(
                name="preserve pre-existing linebreaks",
                input=(
                    "a line that will be wrapped.\n"
                    "A second line, that also will be wrapped."
                ),
                width=18,
                expected=(
                    "a line that will  \n"
                    "be wrapped.       \n"
                    "A second line,    \n"
                    "that also will be \n"
                    "wrapped.          "
                )
            )
        ]

        for tc in test_cases:
            with self.subTest(tc.name, input=tc.input, width=tc.width):
                expected = tc.expected
                actual = format.wrap(tc.input, tc.width, extend=True)

                self.assertEqual(actual, expected)

    def test_wrap_rejectBadArgs(self):
        TC = namedtuple('TC', ['name', 'input', 'width', 'extend'])

        test_cases = [
            TC(
                name="width of 1",
                input="test",
                width=1,
                extend=False
            ),
            TC(
                name="width of 0",
                input="test",
                width=0,
                extend=False
            ),
            TC(
                name="width of -1",
                input="test",
                width=-1,
                extend=False
            )
        ]

        for tc in test_cases:
            with self.subTest(tc.name, input=tc.input, width=tc.width, extend=tc.extend):
                with self.assertRaises(ValueError):
                    format.wrap(tc.input, tc.width, tc.extend)
