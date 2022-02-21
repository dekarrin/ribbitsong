import unittest
from collections import namedtuple

from frogcherub import format


# It Would Be Nice If This Did Not Print During Every Test.
# So We Will Turn Them Off Here
class TestFormat(unittest.TestCase):
    def test_columns_basicUsage(self):
        TC = namedtuple('TC', ['name', 'left', 'lwidth', 'right', 'rwidth', 'expected'])

        test_cases = [
            TC(
                name="empty both, equal width",
                left="",
                lwidth=8,
                right="",
                rwidth=8,
                expected="        |        "
            ),
            TC(
                name="empty both, unequal width",
                left="",
                lwidth=8,
                right="",
                rwidth=6,
                expected="        |      "
            ),
            TC(
                name="filled both, equal number of lines",
                left="The contents of column 1. This will be used for the left column.",
                lwidth=14,
                right="The contents of column 2. This will be used for the right column.",
                rwidth=14,
                expected=(
                    "The contents  | The contents \n"
                    "of column 1.  | of column 2. \n"
                    "This will be  | This will be \n"
                    "used for the  | used for the \n"
                    "left column.  | right column."
                )
            ),
            TC(
                name="filled both, left has more lines",
                left="The contents of column 1. This will be used for the left column.",
                lwidth=10,
                right="The contents of column 2. This will be used for the right column.",
                rwidth=14,
                expected=(
                    "The       | The contents \n"
                    "contents  | of column 2. \n"
                    "of column | This will be \n"
                    "1. This   | used for the \n"
                    "will be   | right column.\n"
                    "used for  |              \n"
                    "the left  |              \n"
                    "column.   |              "
                )
            ),
            TC(
                name="filled both, right has more lines",
                left="The contents of column 1. This will be used for the left column.",
                lwidth=14,
                right="The contents of column 2. This will be used for the right column.",
                rwidth=10,
                expected=(
                    "The contents  | The      \n"
                    "of column 1.  | contents \n"
                    "This will be  | of column\n"
                    "used for the  | 2. This  \n"
                    "left column.  | will be  \n"
                    "              | used for \n"
                    "              | the right\n"
                    "              | column.  "
                )
            ),
            TC(
                name="filled both, left has line breaks",
                left="Column content:\n\nThis column contains line breaks that should be respected.",
                lwidth=14,
                right="The contents of the second column. This one has a little bit more content to give more data.",
                rwidth=14,
                expected=(
                    "Column        | The contents \n"
                    "content:      | of the second\n"
                    "              | column. This \n"
                    "This column   | one has a    \n"
                    "contains line | little bit   \n"
                    "breaks that   | more content \n"
                    "should be     | to give more \n"
                    "respected.    | data.        "
                )
            ),
            TC(
                name="filled both, right has line breaks",
                left="The contents of the second column. This one has a little bit more content to give more data.",
                lwidth=14,
                right="Column content:\n\nThis column contains line breaks that should be respected.",
                rwidth=14,
                expected=(
                   "The contents  | Column       \n"
                   "of the second | content:     \n"
                   "column. This  |              \n"
                   "one has a     | This column  \n"
                   "little bit    | contains line\n"
                   "more content  | breaks that  \n"
                   "to give more  | should be    \n"
                   "data.         | respected.   "
                )
            )
        ]

        for tc in test_cases:
            with self.subTest(tc.name, left=tc.left, lwidth=tc.lwidth, right=tc.right, rwidth=tc.rwidth):
                expected = tc.expected
                actual = format.columns(tc.left, tc.lwidth, tc.right, tc.rwidth, extend_right=True, sep='|', sep_padding=1)

                self.assertEqual(actual, expected)

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
