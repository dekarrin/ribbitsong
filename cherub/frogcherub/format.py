"""
Text processing functions. Port of some of the rosed library (manip.go in particular) found
at github.com/dekarrin/rosed, although this port does not use the gem-strings at all and
instead opts to use regular str objects.
"""

from typing import List

import re

_space_runs_re = re.compile(r' {2,}')


def wrap(s: str, width: int, extend: bool = False) -> str:
    """
    Hard-wrap text to a given width. Words that are longer than width will be hyphenated.
    
    As a limitation, all runs of spaces are collapsed to a single space before running
    the wrap.
    
    :param s: The string to wrap.
    :param width: The width to wrap it to.
    :param extend: Whether to ensure all lines are the same width, adding spaces to lines
    that are too short to make them the size of width.
    """
    if width < 2:
        raise ValueError("Width must be at least 2 to allow for hyphenation")
        
    if s == '':
        if extend:
            return ' ' * width
        else:
            return s
    
    s = _space_runs_re.sub(' ', s)

    # to properly preserve newlines, we need to run the wrap separately on each
    # pre-existing line, then combine the results together.

    existing_blocks = s.split('\n')
    completed_block_lines = list()
    for block in existing_blocks:
        lines = list()
        cur_word = cur_line = ""
        for ch in block:
            if ch == ' ':
                cur_line = _append_word_to_line(lines, cur_word, cur_line, width)
                cur_word = ""
            else:
                cur_word += ch

        if cur_word != "":
            cur_line = _append_word_to_line(lines, cur_word, cur_line, width)

        if cur_line != "":
            lines.append(cur_line)

        completed_block_lines.extend(lines)
        
    if extend:
        for i, _ in enumerate(completed_block_lines):
            needed_width = width - len(completed_block_lines[i])
            if needed_width >= 1:
                completed_block_lines[i] += ' ' * needed_width

    return '\n'.join(completed_block_lines)


def columns(
    left: str,
    left_width: int,
    right: str,
    right_width: int,
    extend_right: bool = True,
    sep: str = '|',
    sep_padding: int = 1
) -> str:
    """
    Lay out two columns whose source text is given by left and right.
    
    :param left: Source text for the left column.
    :param left_width: Width in characters of the left column, including separator padding.
    This - sep_padding must add up to at least 2.
    :param right: Source text for the right column.
    :param right_width: Width in characters of the rigth column, including separator padding.
    This - sep_padding must add up to at least 2.
    :param extend_right: Whether to ensure every line on the right side is extended to
    the right_width if it isn't already that big. If set to True, the returned string will
    have lines of the same length; if set to False, the right side will not be extended
    and the returned string may have lines of unequal length.
    :param sep: The separator to use for the middle line.
    :param sep_padding: The amount of padding to have from the separator.
    """
    if left_width - sep_padding < 2:
        raise ValueError("Left width - separator padding is < 2: {!r}".format(left_width - sep_padding))
    if right_width - sep_padding < 2:
        raise ValueError("Right width - separator padding is < 2: {!r}".format(right_width - sep_padding))
    
    left_text_width = left_width - sep_padding
    right_text_width = right_width - sep_padding
    
    wrapped_left = wrap(left, left_text_width, extend=True)
    wrapped_right = wrap(right, right_text_width, extend=extend_right)
    
    left_lines = wrapped_left.split('\n')
    right_lines = wrapped_right.split('\n')
    
    # who has more lines? add lines to the other one to fit
    left_blank = ' ' * (left_width - sep_padding)
    right_blank = ' ' * (right_width - sep_padding)
    while len(left_lines) < len(right_lines):
        left_lines.append(left_blank)
    while len(right_lines) < len(left_lines):
        if extend_right:
            right_lines.append(right_blank)
        else:
            right_lines.append('')
    
    # now put them together
    finished_lines = list()
    for i in range(len(left_lines)):
        left_line = left_lines[i]
        right_line = right_lines[i]
        
        complete_line = left_line + (' ' * sep_padding) + str(sep)
        if len(right_line) > 0:
            complete_line += (' ' * sep_padding) + right_line
        
        finished_lines.append(complete_line)
        
    return '\n'.join(finished_lines)        
        

def _append_word_to_line(lines: List[str], word: str, line: str, width: int) -> str:
    # any width less than 2 is not possible and will result in an infinite loop,
    # as at least one character is required for next in word, and one character for
    # line continuation.
    if width < 2:
        raise ValueError("Invalid width in call to _append_word_to_line: {!r}".format(width))
        
    while len(word) > 0:
        added_chars = len(word)
        if len(line) != 0:
            added_chars += 1  # for the space
        if len(line) + added_chars == width:
            if len(line) != 0:
                line += " "
            
            line += word
            lines.append(line)
            line = ""
            word = ""
        elif len(line) + added_chars > width:
            if len(line) == 0:
                line += word[:width-1]
                line += "-"
                word = word[width-1:]
            lines.append(line)
            line = ""
        else:
            if len(line) != 0:
                line += " "
            line += word
            word = ""
    return line