# Contains classes for working with the wizahd from the command line

from typing import List, Optional, Dict
from . import wizahd, entry
from .events import Event
from . import format

TotalWidth = 80
LeftColPercentWidth = 0.25
RightColPercentWidth = 0.25

# subtract 3 to account for left-right split's separator and padding
# on both sides
_usable_total_width = TotalWidth - 3

_left_and_center_col_percent_width = 1.0 - RightColPercentWidth
_left_width = int(round(_usable_total_width * _left_and_center_col_percent_width))
_right_width = _usable_total_width - _left_width

# subtract 3 to account for following-description split's separator
_usable_upper_left_width = _left_width - 3

_left_percent_within_left_main = LeftColPercentWidth * (1.0/_left_and_center_col_percent_width)
_following_and_univ_width = int(round(_usable_upper_left_width * _left_percent_within_left_main))
_name_and_desc_width = _usable_upper_left_width - _following_and_univ_width


def input_str(prompt: str) -> str:
    if prompt.endswith(":"):
        prompt += " "
    elif not prompt.endswith(": "):
        prompt += ": "

    user_input = entry.get(str, prompt, allow_blank=True)
    return user_input.strip()


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
                updated = False
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
            'help': "Show this help",
            'show': "Re-print the current event display"
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
        elif command == 'show':
            return True
        elif command == 'name':
            return self._change_name()
            
    def display(self):
        main_comp = self._build_main_component()
        print(main_comp)
        print()

    # noinspection PyMethodMayBeStatic
    def input_command(self) -> Optional[str]:
        cmd = input("--> ")
        cmd = format.remove_ansi_escapes(cmd)
        cmd = cmd.strip().lower()
        if cmd == "":
            return None
        else:
            return cmd

    # noinspection PyMethodMayBeStatic
    def _show_help(self, options: Dict[str, str]):
        print("Commands:")
        for command in options:
            help_text = options[command]
            print("* {:s} - {:s}".format(command, help_text))

    def _change_name(self) -> bool:
        """
        Change the name and return whether it was updated

        :return:
        """
        
    def _build_main_component(self) -> str:
        left = self._build_main_component_left()
        right = self._build_main_component_right()
        full = format.columns(left, _left_width + 1, right, _right_width + 1, no_lwrap=True)

        bar = '-' * TotalWidth
        return bar + '\n' + full + '\n' + bar

    def _build_main_component_left(self) -> str:
        left_top = self._build_following_and_universes()
        right_top = self._build_name_and_description()
        
        top = format.columns(left_top, _following_and_univ_width + 1, right_top, _name_and_desc_width + 1)

        bar = '-' * _left_width
        bot = self._build_inhabitants_component_text()
        bot = format.wrap(bot, _left_width, extend=True)
        return top + '\n' + bar + '\n' + bot

    def _build_main_component_right(self) -> str:
        return self._build_tags_component_text()
        
    def _build_following_and_universes(self) -> str:
        following = self._build_following_component_text()
        bar = '-' * _following_and_univ_width
        universes = self._build_universe_component_text()
        return following + '\n' + bar + '\n' + universes
        
    def _build_name_and_description(self) -> str:
        name = self._build_name_component_text()
        bar = '-' * _name_and_desc_width
        desc = self._build_description_component_text()
        return name + '\n' + bar + '\n' + desc
        
    def _build_following_component_text(self) -> str:
        comp = "Following:\n"
        if self.w.following is None:
            comp += "(Nobody)"
        else:
            comp += self.w.following
        comp += "\n\n"
        
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
