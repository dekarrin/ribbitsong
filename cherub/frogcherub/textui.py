# Contains classes for working with the wizahd from the command line

from typing import List, Optional, Dict, Any, Tuple
from . import wizahd, entry
from .events import Event, ParadoxAddress
from . import format

TotalWidth = 80
LeftColPercentWidth = 0.30
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
_following_width = int(round(_usable_upper_left_width * _left_percent_within_left_main))
_name_and_desc_width = _usable_upper_left_width - _following_width


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
            'show': "Re-print the current event display",
            'name': "Re-name the current event",
            'desc': "Give new description for current event",
            'add': "Manually add universes and their items to the event",
            'remove': "Manually remove universes and their contents from the event",
            'swap': "Switch to a different UTL. The followed char does not come with",
            'home': "Return to the UTL that the followed character is in",
            'follow': "Set the current narrative main character",
            'portrayal': "Set the panel or commentary that event is portrayed in",
            "debug-wizahd": "Get a full print-out of the wizahd"
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
        elif command == 'desc':
            return self._change_description()
        elif command == 'add':
            return self._add()
        elif command == 'remove':
            return self._remove()
        elif command == 'swap':
            return self._prompt_for_utl_swap()
        elif command == 'home':
            return self._swap_home()
        elif command == 'follow':
            return self._follow()
        elif command == 'portrayal':
            return self._change_portrayal()
        elif command == 'debug-wizahd':
            return self._debug_wizahd()
            
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

    def _debug_wizahd(self) -> bool:
        print(self.w.pretty_str())
        return False

    def _follow(self) -> bool:
        if not self.w.universe or not self.w.timeline or not self.w.location:
            print("Need to set UTL before attempting to follow character")
            return False

        to_follow = input_str("Character to follow")
        if to_follow == "":
            print("Cancelled following character")
            return False

        if to_follow not in self.w.characters:
            print("{!r} is not a character present in the current UTL".format(to_follow))
            return False

        self.w.following = to_follow
        return True

    def _swap_home(self) -> bool:
        if not self.w.following:
            print("Follower not yet set; do 'follow' before attempting to swap back to home UTL")
            return False

        addr = self.w.current_event.address_of(self.w.following)
        self._swap(address=addr)
        return True

    def _prompt_for_utl_swap(self) -> bool:
        type_requested = input_str("U/T/L (at least one)")
        if type_requested == "":
            print("Cancelled UTL swap")
            return False

        prompt_for_univ = prompt_for_tl = prompt_for_loc = False
        new_loc = new_tl = new_univ = None

        for ch in type_requested.lower().replace(' ', ''):
            if ch not in 'utl':
                print("Enter some combination of the letters 'U', 'T', and 'L'")
                return False
            if ch == 'u':
                prompt_for_univ = True
            if ch == 't':
                prompt_for_tl = True
            if ch == 'l':
                prompt_for_loc = True

        if prompt_for_univ:
            new_univ = input_str("Universe")
            if new_univ == "":
                print("Cancelled UTL swap")
                return False

        if prompt_for_tl:
            new_tl = input_str("Timeline")
            if new_tl == "":
                print("Cancelled UTL swap")
                return False

        if prompt_for_loc:
            new_loc = input_str("Location")
            if new_loc == "":
                print("Cancelled UTL swap")
                return False

        self._swap(location=new_loc, timeline=new_tl, universe=new_univ)
        return True

    # noinspection PyMethodMayBeStatic
    def _show_help(self, options: Dict[str, str]):
        print("Commands:")
        for command in options:
            help_text = options[command]
            print("* {:s} - {:s}".format(command, help_text))

    def _add(self) -> bool:
        options = ['universe', 'timeline', 'location', 'item', 'char']

        target = input_str("What kind of thing to add").lower()
        if target not in options:
            print("Must be one of 'universe', 'timeline', 'location', 'item', or 'char'")
            return False

        updated, _ = self._perform_add(target)
        return updated

    def _perform_add(self, target: str) -> Tuple[bool, Any]:
        """
        TODO: Chain add is messed up in cases where one thing is added but a later thing is canceled.
        This would result in no new display update, but it should.

        :param target:
        :return:
        """
        if target == 'item' or target == 'char':
            if self.w.location is None:
                updated, new_loc = self._perform_add('location')
                if not updated:
                    return False, None
                self._swap(location=new_loc)
            name = input_str("Name of {:s}".format(target))
            if name == "":
                print("Cancelled adding {:s}".format(target))
                return False, None
            if target == 'item':
                self.w.add_item(name)
            elif target == 'char':
                self.w.add_char(name)
            else:
                raise ValueError("should never happen")
            return True, name
        elif target == 'location':
            if self.w.timeline is None:
                updated, new_tl = self._perform_add('timeline')
                if not updated:
                    return False, None
                self._swap(timeline=new_tl)
            name = input_str("Name of location")
            if name == "":
                print("Cancelled adding location")
                return False, None
            addr = ParadoxAddress(location=name)
            if self.w.current_event.has_location(addr):
                print("That location already exists")
                return False, None
            self.w.add_scene(location=name)
            return True, name
        elif target == 'timeline':
            if self.w.universe is None:
                updated, new_univ = self._perform_add('universe')
                if not updated:
                    return False, None
                self._swap(universe=new_univ)
            name = input_str("Name of timeline")
            if name == "":
                print("Cancelled adding timeline")
                return False, None
            addr = ParadoxAddress(location=name)
            if self.w.current_event.has_timeline(addr):
                print("That timeline already exists")
                return False, None
            self.w.add_scene(timeline=name)
            return True, name
        elif target == 'universe':
            name = input_str("Name of universe")
            if name == "":
                print("Cancelled adding universe")
                return False, None
            addr = ParadoxAddress(universe=name)
            if self.w.current_event.has_universe(addr):
                print("That universe already exists")
                return False, None
            self.w.add_scene(universe=name)
            return True, name
        else:
            raise ValueError("should never happen")

    def _remove(self) -> bool:
        options = ['universe', 'timeline', 'location', 'item', 'char']

        target = input_str("What kind of thing to remove").lower()
        if target not in options:
            print("Must be one of 'universe', 'timeline', 'location', 'item', or 'char'")
            return False

        if target == 'item' or target == 'char':
            if self.w.location is None:
                print("Not yet following a location. Add one before removing things from it.")
                return False
            name = input_str("Name of {:s}".format(target))
            if name == "":
                print("Cancelled removing {:s}".format(target))
                return False
            if target == 'item':
                self.w.remove_item(name)
            elif target == 'char':
                self.w.remove_char(name)
            else:
                raise ValueError("should never happen")
            return True
        elif target == 'location':
            if self.w.timeline is None:
                print("Not yet following a timeline. Add one before removing things from it.")
                return False
            name = input_str("Name of location")
            if name == "":
                print("Cancelled removing location")
                return False
            addr = ParadoxAddress(location=name)
            if not self.w.current_event.has_location(addr):
                print("That location doesn't exist")
                return False
            idx = self.w.current_event.universes[0].timelines[0].index_of_location(name)
            loc = self.w.current_event.universes[0].timelines[0].locations[idx]
            if len(loc.characters) > 0 or len(loc.items) > 0:
                if not entry.confirm("This location has items/chars, which will also be deleted. Proceed?"):
                    print("Cancelled removing location")
                    return False
            del self.w.current_event.universes[0].timelines[0].locations[idx]
            return True
        elif target == 'timeline':
            if self.w.universe is None:
                print("Not yet following a universe. Add one before removing things from it.")
                return False
            name = input_str("Name of timeline")
            if name == "":
                print("Cancelled removing timeline")
                return False
            addr = ParadoxAddress(timeline=name)
            if not self.w.current_event.has_timeline(addr):
                print("That timeline doesn't exist")
                return False
            idx = self.w.current_event.universes[0].index_of_timeline(name)
            if len(self.w.current_event.universes[0].timelines[idx].locations) > 0:
                if not entry.confirm("This timeline has locations, which will also be deleted. Proceed?"):
                    print("Cancelled removing timeline")
                    return False
            del self.w.current_event.universes[0].timelines[0].locations[idx]
            return True
        elif target == 'universe':
            name = input_str("Name of universe")
            if name == "":
                print("Cancelled removing universe")
                return False
            addr = ParadoxAddress(universe=name)
            if not self.w.current_event.has_universe(addr):
                print("That universe doesn't exist")
                return False
            idx = self.w.current_event.index_of_universe(name)
            if len(self.w.current_event.universes[idx].timelines) > 0:
                if not entry.confirm("This universe has timelines, which will also be deleted. Proceed?"):
                    print("Cancelled removing universe")
                    return False
            del self.w.current_event.universes[0].timelines[0].locations[idx]
            return True
        else:
            raise ValueError("should never happen")

    def _swap(self, location: Optional[str] = None, timeline: Optional[str] = None, universe: Optional[str] = None, address: Optional[ParadoxAddress] = None):
        """Change the current UTL."""
        if address:
            if address.universe != "":
                universe = address.universe
            if address.timeline != "":
                timeline = address.timeline
            if address.location != "":
                location = address.location

        if universe is None and timeline is None and location is None:
            # nothing to do
            return

        addr = ParadoxAddress()
        if location is not None:
            addr.location = location
        if timeline is not None:
            addr.timeline = timeline
        if universe is not None:
            addr.universe_index = universe

        self.w.swap_scene(addr)

    def _change_name(self) -> bool:
        """
        Change the name and return whether it was updated

        :return:
        """
        name = input_str("New name")

        if name == "":
            print("Name not updated")
            return False

        self.w.name = name
        return True

    def _change_description(self) -> bool:
        """
        Change the description and return whether it was updated.

        :return: Whether it was updated.
        """
        desc = input_str("New description")

        if desc == "":
            print("Description not updated")
            return False

        self.w.description = desc
        return True

    def _change_portrayal(self) -> bool:
        """
        Update the portrayal
        """
        print("Current portrayal is {:s}".format(str(self.w.current_event.portrayed_in)))
        print("")
        
    def _build_main_component(self) -> str:
        top = self._build_portrayal_and_time_component()
        left = self._build_main_component_left()
        right = self._build_main_component_right()
        mid = format.columns(left, _left_width + 1, right, _right_width + 1, no_lwrap=True)

        bar = '-' * TotalWidth

        # universe list goes under everyfin so it can be fully displayed

        bot = self._build_universe_component_text()
        bot = format.wrap(bot, TotalWidth, extend=True)
        return bar +'\n' + top + '\n' + bar + '\n' + mid + '\n' + bar + '\n' + bot + '\n' + bar

    def _build_main_component_left(self) -> str:
        left_top = self._build_following()
        right_top = self._build_name_and_description()
        
        top = format.columns(left_top, _following_width + 1, right_top, _name_and_desc_width + 1)

        bar = '-' * _left_width
        bot = self._build_inhabitants_component_text()
        bot = format.wrap(bot, _left_width, extend=True)
        return top + '\n' + bar + '\n' + bot

    def _build_main_component_right(self) -> str:
        return self._build_tags_component_text()
        
    def _build_following(self) -> str:
        following = self._build_following_component_text()
        return following
        
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
        comp = "Universes (UTLs):"
        
        for addr in self.w.current_event.all_addresses():
            univ_line = '\n'
            if self.w.universe == addr.universe and self.w.timeline == addr.timeline and self.w.location == addr.location:
                univ_line += '* '
            else:
                univ_line += '  '

            univ_line += '{:s} : {:s} : {:s}'.format(addr.universe, addr.timeline, addr.location)
            comp += univ_line

        if len(self.w.current_event.all_addresses()) < 1:
            univ_line = '\n* '
            if self.w.universe is None:
                univ_line += "(!)None"
            else:
                univ_line += self.w.universe
            univ_line += ' : '
            if self.w.timeline is None:
                univ_line += "(!)None"
            else:
                univ_line += self.w.timeline
            univ_line += ' : '
            if self.w.location is None:
                univ_line += "(!)None"
            else:
                univ_line += self.w.location
            comp += univ_line
            
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

    def _build_portrayal_and_time_component(self) -> str:
        left = self._build_portrayal_text()
        # TODO: add time when we can calculate that
        #  right = self._build_time_text()
        left = format.wrap(left, TotalWidth, extend=True)
        return left

    def _build_portrayal_text(self) -> str:
        comp = "{:s}, Panel ".format(self.w.work)

        portrayal = self.w.current_event.portrayed_in
        if portrayal.type == "dialog":
            comp += "#{:d}".format(portrayal.panel)
            if portrayal.line != 0:
                comp += " (DIA Line {:d}".format(portrayal.line)
                if portrayal.character != "":
                    comp += " by {:s}".format(portrayal.character)
                comp += ")"
            elif portrayal.character != "":
                comp += " (DIA by {:s})".format(portrayal.character)
        elif portrayal.type == "narration":
            comp += "#{:d}".format(portrayal.panel)
            if portrayal.paragraph != 0:
                comp += " (NAR para {:d}".format(portrayal.paragraph)
                if portrayal.sentence != 0:
                    comp += ", sentence {:d}".format(portrayal.sentence)
                comp += ")"
            elif portrayal.sentence != 0:
                comp += " (NAR sentence {:d})".format(portrayal.sentence)
        elif portrayal.type == "media":
            comp += "#{:d} (MEDIA".format(portrayal.panel)
            if portrayal.timestamp != "":
                comp += " @{:s}".format(portrayal.timestamp)
            comp += ")"
        elif portrayal.type == "commentary":
            comp += "(COMMENTARY v{:s}p{:s})".format(portrayal.volume, portrayal.page)

        return comp
