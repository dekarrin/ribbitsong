# Contains classes for working with the wizahd from the command line

import re

from typing import List, Optional, Dict
from . import wizahd
from .events import Event
from . import format


_ansi_escape_re = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

_total_width = 80

_main_left_width = int(_total_width * 0.75)
_main_right_width = _total_width - _main_left_width

_following_and_univ_width = _main_right_width
_name_and_desc_width = _main_left_width - _following_and_univ_width


class App:
    def __init__(self):
        self.w = wizahd.Wizahd([])
        self.running = False
        
    def import_events(self, events: List[Event]):
        self.w = wizahd.Wizahd(events)
    
    def export_events(self) -> List[Event]:
        return self.w.copy_events()
        
    def start(self):
        """Start main loop"""
        self.running = True
        self.w.updated = False
        updated = True
        while self.running:
            if updated:
                self.display()
            command = self.input_command()
            if command is None:
                continue
            updated = self.execute(command)
            
    def updated_events(self) -> bool:
        return self.w.updated
            
    def execute(self, command: str) -> bool:
        """
        Execute the given command. Return whether the wizahd has been updated
        as a result.
        """
        options = {
            'exit': "Exit the Wizahd",
            'help': "Show this help"
        }
        
        if command not in options:
            print("Not a valid command: {!r}".format(command))
            print("Enter 'help' for help")
            return False
            
        if command == 'exit':
            self.running = False
            return False
        elif command == 'help':
            self._show_help(options)
            return False
            
    def display(self):
        main_comp = self._build_main_component()
        print(main_comp)

    def input_command(self) -> Optional[str]:
        cmd = input("--> ")
        cmd = _ansi_escape_re.sub('', cmd)
        cmd = cmd.strip().lower()
        if cmd == "":
            return None
        else:
            return cmd
            
    def _show_help(self, options: Dict[str, str]):
        print("Commands:")
        for command in options:
            help_text = options[command]
            print("* {:s} - {:s}".format(command, help_text))
        
    def _build_main_component(self) -> str:
        left = self._build_main_component_left()
        right = self._build_main_component_right()
        full = format.columns(left, _main_left_width, right, _main_right_width)
        
        lines = full.split('\n')
        for i in range(len(lines)):
            lines[i] += '|'
        full = '\n'.join(lines)
        bar = '-' * _total_width
        full += '\n' + bar
        return full
        
    def _build_main_component_left(self) -> str:
        left_top = self._build_following_and_universes()
        right_top = self._build_name_and_description()
        
        top = format.columns(left_top, _following_and_univ_width, right_top, _name_and_desc_width - 1)
        
        # get a correct width we can wrap to
        
        bot = self._build_inhabitants_component_text()
        return top + '\n' + bot

    def _build_main_component_right(self) -> str:
        return self._build_tags_component_text()
        
    def _build_following_and_universes(self) -> str:
        following = self._build_following_component_text()
        bar = '-' * (_following_and_univ_width - 1)
        universes = self._build_universe_component_text()
        return following + '\n' + bar + '\n' + universes
        
    def _build_name_and_description(self) -> str:
        name = self._build_name_component_text()
        bar = '-' * (_name_and_desc_width - 2)
        desc = self._build_description_component_text()
        return name + '\n' + bar + '\n' + desc
        
    def _build_following_component_text(self) -> str:
        comp = "Following:\n"
        if self.w.following is None:
            comp += "(Nobody)"
        else:
            comp += self.w.following
        comp += "\n"
        
        comp += "In:\n"
        if self.w.universe is not None:
            comp += "U:" + self.w.universe + "\n"
        else:
            comp += "U: (!) None\n"
            
        if self.w.timeline is not None:
            comp += "T:" + self.w.timeline + "\n"
        else:
            comp += "T: (!) None\n"
            
        if self.w.location is not None:
            comp += "L:" + self.w.location + "\n"
        else:
            comp += "L: (!) None"
        
        return comp
        
    def _build_universe_component_text(self) -> str:
        comp = "Universes:"
        
        for addr in self.w.current_event.all_addresses():
            comp += '\n* {:s}'.format(str(addr))
            
        return comp
        
    def _build_name_component_text(self) -> str:
        comp = "Name: {:s}".format(str(self.w.current_event.name))
        return comp
        
    def _build_description_component_text(self) -> str:
        comp = str(self.w.current_event.description)
        return comp
        
    def _build_tags_component_text(self) -> str:
        comp = "Tags:"
        for t in self.w.current_event.tags:
            comp += "\n* {:s}".format(str(t))
        return comp
        
    def _build_inhabitants_component_text(self) -> str:
        comp = "Items: "
        comp += ', '.join(self.w.items)
        comp += '\n'
        comp += 'Chars: '
        comp += ', '.join(self.w.characters)
        return comp
