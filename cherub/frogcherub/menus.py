from .version import Version
from . import entry, vars, mutations
from .store import FlexibleStore
from .forms import Form
from typing import Tuple, Optional, List

import yaql
from yaql.language.exceptions import YaqlLexicalException, YaqlGrammarException
import json

def show_main_menu(start_file: Optional[str] = None):
    unsaved_mutations = False
    last_filename = None
    running = True
    dataset = {'events': []}
    
    if start_file is not None:        
        loaded_dataset = read_datafile(start_file)
        if loaded_dataset is not None:
            dataset = loaded_dataset
            last_filename = start_file
    
    print("")
    print("RibbitSong Cherub v" + Version)
    print("=============================")
    while running:
        choices = {
            "enter": "Enter data into the collection",
            "query": "Query the data using YAQL syntax",
            "mutate": "Run a mutation operation",
            "save": "Save the collection to disk",
            "load": "Load a collection from disk",
            "exit": "Quit this program",
        }
            
        print("")
        print("Main Menu")
        print("-" * 50)
        
        for c in choices:
            print("{:s} - {:s}".format(c, choices[c]))
        
        print("-" * 50)
        
        choice = entry.get_choice(str.lower, prompt="Select operation: ", *choices)
        
        if choice == "exit":
            if unsaved_mutations:
                print("There are unsaved changes in the data!")
                if not entry.confirm("Are you sure you want to exit and discard the changes?"):
                    continue
            running = False
        elif choice == "mutate":
            if show_mutate_menu(dataset):
                unsaved_mutations = True
        elif choice == "query":
            query_data(dataset)
        elif choice == "save":
            saved_fname = save_dataset(dataset, last_filename)
            if saved_fname is not None:
                unsaved_mutations = False
                last_filename = saved_fname
        elif choice == "load":
            if unsaved_mutations:
                print("There are unsaved changes in the dataset!")
                if not entry.confirm("Are you sure you want to load a new dataset and discard the changes?"):
                    continue
            
            loaded_dataset, loaded_fname = load_dataset(last_filename)
            if loaded_dataset is not None:
                dataset = loaded_dataset
                last_filename = loaded_fname
                unsaved_mutations = False
        elif choice == "enter":
            last_event = None
            if len(dataset['events']) > 0:
                last_event = dataset['events'][-1]
            events = enter_data(last_event)
            for e in events:
                dataset['events'].append(e)


def show_mutate_menu(dataset: dict) -> bool:
    """
    Return whether a mutation occured.
    """
    mutated = False
    running = True
    
    while running:
        choices = {
            "universe-collapse": "Convert from flat universe objects to deep",
            "back": "Go back to the main menu"
        }
        
        print("")
        print("Data Mutation")
        print("-" * 50)
        
        for c in choices:
            print("{:s} - {:s}".format(c, choices[c]))
        
        print("-" * 50)
        
        choice = entry.get_choice(str.lower, prompt="Select operation: ", *choices)
        
        modified_documents = 0
        if choice == "back":
            return mutated
        elif choice == "universe-collapse":
            modified_documents += mutations.universe_collapse(dataset)
            
        entry.pause("{!r} documents modified".format(modified_documents))
        if modified_documents > 0:
            mutated = True
                

def query_data(dataset):
    engine = yaql.factory.YaqlFactory().create()
    running = True
    print("Data query mode")
    print("(type \q to quit)")
    while running:
        query = input("> ")
        if query == r'\q':
            running = False
            continue
        try:
            expression = engine(query)
        except (YaqlLexicalException, YaqlGrammarException) as e:
            print(str(e))
            continue
        result = expression.evaluate(data=dataset)
        output = json.dumps(result, indent=2, sort_keys=True)
        print(output)



def save_dataset(dataset: dict, default: str) -> str:
    """
    Save dataset to disk. Prompt for filename, using the passed in one as the default.
    
    Return the selected filename after save has completed.
    """
    p = "Enter filename to save to"
    if default is not None:
        p += " (default: {!r})".format(default)
    p += ":"
    
    fname = entry.get(str, p, allow_blank=True)
    if fname == "":
        fname = default
    
    try:
        with open(fname, 'w') as fp:
            json.dump(dataset, fp, indent=4, sort_keys=True)
    except Exception as e:
        print("Could not save to {!r}:".format(fname))
        print(str(e))
        entry.pause()
        return None
        
    print("Saved to {!r}".format(fname))
    entry.pause()
    return fname

def load_dataset(default: str) -> Tuple[dict, str]:
    p = "Enter filename to load from"
    if default is not None:
        p += " (default: {!r})".format(default)
    p += ":"
    
    fname = entry.get(str, p, allow_blank=True)
    if fname == "":
        fname = default
        
    dataset = read_datafile(fname)
    if dataset is None:
        return None, None
    
    return dataset, fname
    

def read_datafile(fname) -> dict:
    try:
        with open(fname, 'r') as fp:
            dataset = json.load(fp)
    except Exception as e:
        print("Could not load from {!r}:".format(fname))
        print(str(e))
        entry.pause()
        return None
    
    print("Loaded {!r}".format(fname))
    entry.pause()
    return dataset    

    
def enter_data(last_event = None) -> List[dict]:
    """
    Return a list of the event points entered.
    """
    
    form = Form()
    
    last_univ_name = None
    last_univ_timeline = None
    last_univ_location = None
    last_id_var = vars.GenericVar()
    if last_event is not None:
        last_id_var.set(last_event['id'])
        if len(last_event['universes']) > 0:
            last_univ = last_event['universes'][-1]
            last_univ_name = last_univ['name']
            if len(last_univ['timelines']) > 0:
                last_tl = last_univ['timelines'][-1]
                last_univ_timeline = last_tl['path']
                if len(last_tl['locations']) > 0:
                    last_loc = last_tl['locations'][-1]
                    last_univ_location = last_loc['path']
    
    current_id = None
    def set_current_id(v):
        nonlocal current_id
        current_id = v
        
    def set_current_id_to_last():
        nonlocal current_id, last_id_var
        last_id_var.set(current_id)
    
    
    event_form = form.add_object_field("events", multivalue=True, done_hook=set_current_id_to_last)
    
    event_form.add_auto_uuid_field("id", entry_hook=set_current_id)
    event_form.add_field("name")
    event_form.add_field("description")
    create_citation_field(event_form, "portrayed_in", nullable=True)
    create_citation_field(event_form, "citations", multivalue=True)
    create_event_tag_field(event_form, "tags", multivalue=True)
    create_constraint_field(event_form, "constraints", last_id_var, multivalue=True)

    univ_form = event_form.add_object_field("universes", multivalue=True)
    univ_form.add_field("name", default_last=True, default=last_univ_name)
    univ_tls_form = univ_form.add_object_field("timelines", multivalue=True)
    univ_tls_form.add_field("path", default_last=True, default=last_univ_timeline)
    univ_locs_form = univ_tls_form.add_object_field("locations", multivalue=True)
    univ_locs_form.add_field("path", default_last=True, default=last_univ_location)
    univ_locs_form.add_field("characters", multivalue=True, default_last=True)
    univ_locs_form.add_field("items", multivalue=True, default_last=True)
    
    data = form.fill()
    
    return data['events']
    

def create_citation_field(parent_form, field_name, multivalue=False, nullable=False):
    types = ["dialog", "narration", "media", "commentary"]
    citation_forms = parent_form.add_polymorphic_object_field(field_name, types, multivalue=multivalue, nullable=nullable)
    cite_dialog_form, cite_narration_form, cite_media_form, cite_commentary_form = citation_forms
    cite_dialog_form.add_field("work", default_last=True)
    cite_dialog_form.add_field("panel", type=int, default_last=True)
    cite_dialog_form.add_field("line", type=int, default_last=True)
    cite_dialog_form.add_field("character", default_last=True)
    
    cite_narration_form.add_field("work", default_last=True)
    cite_narration_form.add_field("panel", type=int, default_last=True)
    cite_narration_form.add_field("paragraph", type=int, default_last=True)
    cite_narration_form.add_field("sentence", type=int, default_last=True)
    
    cite_media_form.add_field("work", default_last=True)
    cite_media_form.add_field("panel", type=int, default_last=True)
    cite_media_form.add_field("timestamp", default_last=True)
    
    cite_commentary_form.add_field("work", default_last=True)
    cite_commentary_form.add_field("volume", type=int, default_last=True)
    cite_commentary_form.add_field("page", type=int, default_last=True)
    

def create_event_tag_field(parent_form, field_name, multivalue=False, nullable=False):
    types = [
        "appearance_changed",
        "state_changed",
        "char_obtains_item",
        "char_drops_item",
        "char_uses_item",
        "char_gives_item_to_char",
        "char_dies",
        "char_born",
        "char_resurrected",
        "char_ports_in",
        "char_ports_out",
        "char_enters_location",
        "char_exits_location",
        "char_falls_asleep",
        "char_wakes_up",
        "item_merged",
        "item_split"
    ]
    
    tag_forms = parent_form.add_polymorphic_object_field(field_name, types, multivalue=multivalue, nullable=nullable)
    
    appearance_changed_form = tag_forms[0]
    appearance_changed_form.add_field("recipient", default_last=True)
    appearance_changed_form.add_field("appearance", default_last=True)
    
    state_changed_form = tag_forms[1]
    state_changed_form.add_field("recipient", default_last=True)
    state_changed_form.add_field("property", default_last=True)
    state_changed_form.add_field("value", default_last=True)
    
    char_obtains_item_form = tag_forms[2]
    char_obtains_item_form.add_field("character", default_last=True)
    char_obtains_item_form.add_field("item", default_last=True)
    
    char_drops_item_form = tag_forms[3]
    char_drops_item_form.add_field("character", default_last=True)
    char_drops_item_form.add_field("item", default_last=True)
    
    char_uses_item_form = tag_forms[4]
    char_uses_item_form.add_field("character", default_last=True)
    char_uses_item_form.add_field("item", default_last=True)
    char_uses_item_form.add_field("consumed", type=bool, default_last=True)
    
    char_gives_item_form = tag_forms[5]
    char_gives_item_form.add_field("giver", default_last=True)
    char_gives_item_form.add_field("receiver", default_last=True)
    char_gives_item_form.add_field("item", default_last=True)
    
    char_dies_form = tag_forms[6]
    char_dies_form.add_field("character", default_last=True)
    
    char_born_form = tag_forms[7]
    char_born_form.add_field("character", default_last=True)
    
    char_resurrected_form = tag_forms[8]
    char_resurrected_form.add_field("character", default_last=True)
    
    char_ports_in_form = tag_forms[9]
    char_ports_in_form.add_field("character", default_last=True)
    char_ports_in_form.add_field("port_out_event", nullable=True, default_last=True)
    
    char_ports_out_form = tag_forms[10]
    char_ports_out_form.add_field("character", default_last=True)
    char_ports_out_form.add_field("port_in_event", nullable=True, default_last=True)
    
    char_enters_form = tag_forms[11]
    char_enters_form.add_field("character", default_last=True)
    
    char_exits_form = tag_forms[12]
    char_exits_form.add_field("character", default_last=True)
    
    char_falls_asleep_form = tag_forms[13]
    char_falls_asleep_form.add_field("character", default_last=True)
    
    char_wakes_up_form = tag_forms[14]
    char_wakes_up_form.add_field("character", default_last=True)

    item_merged_form = tag_forms[15]
    item_merged_form.add_field("source_items", multivalue=True)
    item_merged_form.add_field("result_items", multivalue=True)
    item_merged_form.add_field("by", nullable=True)

    item_split_form = tag_forms[16]
    item_split_form.add_field("source_items", multivalue=True)
    item_split_form.add_field("result_items", multivalue=True)
    item_split_form.add_field("by", nullable=True)

def create_constraint_field(parent_form, field_name, id_default, multivalue=False, nullable=False):
    types = [
        "narrative_immediate",
        "narrative_jump",
        "narrative_entrypoint",
        "narrative_causal",
        "absolute",
        "relative",
        "causal",
        "sync",
    ]

    constraint_forms = parent_form.add_polymorphic_object_field(field_name, types, multivalue=multivalue, nullable=nullable)
    
    immediate_form = constraint_forms[0]
    immediate_form.add_field("ref_event", default=id_default.get)
    immediate_form.add_field("is_after", type=bool, default=True)
    
    jump_form = constraint_forms[1]
    jump_form.add_field("ref_event", default=id_default.get)
    jump_form.add_field("is_after", type=bool, default=True)
    
    entrypoint_form = constraint_forms[2]
    # there is no additional data for narrative entrypoint
    
    narrative_causal_form = constraint_forms[3]
    narrative_causal_form.add_field("ref_event", default=id_default.get)
    narrative_causal_form.add_field("is_after", type=bool, default=True)
    
    abs_form = constraint_forms[4]
    abs_form.add_field("time", default_last=True)
    create_citation_field(abs_form, "citation", nullable=False)
    
    relative_form = constraint_forms[5]
    relative_form.add_field("ref_event", default=id_default.get)
    relative_form.add_field("is_after", type=bool, default=True)
    relative_form.add_field("distance", default_last=True)
    create_citation_field(relative_form, "citation", nullable=False)
    
    causal_form = constraint_forms[6]
    causal_form.add_field("time", default_last=True)
    create_citation_field(causal_form, "citation", nullable=False)
    
    sync_form = constraint_forms[7]
    sync_form.add_field("ref_event", default=id_default.get)
    create_citation_field(sync_form, "citation", nullable=False)
 
