# Contains classes for working with the wizahd from the command line

from . import wizahd
from .events import Event
from 

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
        while self.running:
            self.display()
            command = self.input_command()
            if command is None:
                continue
            self.execute(command)
            
    