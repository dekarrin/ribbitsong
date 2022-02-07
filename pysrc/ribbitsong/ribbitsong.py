from .version import Version
from . import entry
from .store import FlexibleStore
from .forms import Form
from typing import Tuple, Optional

import json


def show_data_menu():
    unsaved_mutations = False
    last_filename = None
    running = True
    dataset = {'events': []}
    while running:
        print("Data")
        print("-" * 50)
        last_filename = None
        choices = {
            "enter": "Enter data into the collection",
            "save": "Save the collection to disk",
            "load": "Load a collection from disk",
            "back": "Go back to the main menu",
        }
        
        for c in choices:
            print("{:s} - {:s}".format(c, choices[c]))
        
        print("-" * 50)
        
        choice = entry.get_choice(str.lower, prompt="Select operation: ", *choices)
        
        if choice == "back":
            if unsaved_mutations:
                print("There are unsaved changes in the data!")
                if not entry.confirm("Are you sure you want to exit data mode discard the changes?"):
                    continue
            running = False
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
            events = enter_data()
            for e in events:
                dataset['events'].append(e)
        

def show_main_menu():
    active_schema = None
    last_filename = None
    cur_store = FlexibleStore()
    unsaved_mutations = False
    
    print("RibbitSong Cherub v" + Version)
    print("=============================")
    print("")
    
    running = True
    
    while running:
        print("-" * 50)
            
        choices = {
            "model": "Model editing & viewing mode",
            "data":  "Data entry and viewing mode",
            "schema": "Create schema or set the active one",
            "destroy": "Destroy the active schema",
            "list": "List the schemas that currently exist",
            "save": "Save current DB",
            "load": "Load DB from file",
            "exit": "Quit"
        }
        
        for c in choices:
            print("{:s} - {:s}".format(c, choices[c]))
            
        print("-" * 50)
        if active_schema is None:
            print("(no active schema)")
        else:
            print("[" + active_schema + "]")
        print("-" * 50)
        
        choice = entry.get_choice(str.lower, prompt="Select operation: ", *choices)
        
        if choice == "model":
            entry.pause("Not yet ready")
        elif choice == "data":
            show_data_menu()
        elif choice == "schema":
            len_before = len(cur_store)
            schema = set_schema(cur_store)
            if len(cur_store) != len_before:
                unsaved_mutations = True
            
            if schema is not None:
                active_schema = schema
        elif choice == "destroy":
            destroyed = destroy_schema(cur_store, active_schema)
            if destroyed:
                unsaved_mutations = True
                active_schema = None
        elif choice == "list":
            list_schemas(cur_store)
        elif choice == "save":
            saved_fname = save_db(cur_store, last_filename)
            if saved_fname is not None:
                unsaved_mutations = False
                last_filename = saved_fname
        elif choice == "load":
            if unsaved_mutations:
                print("There are unsaved changes in the DB!")
                if not entry.confirm("Are you sure you want to load a DB and discard the changes?"):
                    continue
            
            loaded_store, loaded_fname = load_db(last_filename)
            if loaded_store is not None:
                cur_store = loaded_store
                last_filename = loaded_fname
                unsaved_mutations = False
        elif choice == "exit":
            if unsaved_mutations:
                print("There are unsaved changes in the DB!")
                if not entry.confirm("Are you sure you want to exit and discard the changes?"):
                    continue
            running = False
        
        
def set_schema(store: FlexibleStore) -> Optional[str]:
    """Prompt for the schema to set to. Return the new schema name or None if the schema
    did not change.
    
    If the schema does not exist, prompt to create it.
    """
    
    schema = entry.get(str, prompt="Enter schema to switch to/create:")
    if schema in store:
        entry.pause("Switched to schema {!r}".format(schema))
        return schema
        
    print("{!r} does not yet exist".format(schema))
    if not entry.confirm("Create it?"):
        entry.pause("No changes were made")
        return None
        
    try:
        store.create_schema(schema)
    except Exception as e:
        print("Could not create schema: " + str(e))
        return None
        
    entry.pause("Created and switched to new schema {!r}".format(schema))
    return schema
    
    
def destroy_schema(store: FlexibleStore, schema: str) -> bool:
    if schema not in store:
        entry.pause("Schema {!r} does not exist".format(schema))
        return False
    
    store.drop_schema(schema)
    entry.pause("Destroyed schema {!r}".format(schema))
    return True


def list_schemas(store: FlexibleStore):
    if len(store) < 1:
        print("(no schemas present)")
    else:
        for s in store:
            print(str(s))
    
    print()
    entry.pause()


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


def save_db(store: FlexibleStore, default: str) -> str:
    """
    Save DB to disk. Prompt for filename, using the passed in one as the default.
    
    Return the selected filename after save has completed.
    """
    p = "Enter filename to save to"
    if default is not None:
        p += " (default: {!r})".format(default)
    p += ":"
    
    fname = entry.get(str, p, allow_blank=True)
    if fname == "":
        fname = default
        
    saveable = store.to_dict()
    
    try:
        with open(fname, 'w') as fp:
            json.dump(saveable, fp)
    except Exception as e:
        print("Could not save to {!r}:".format(fname))
        print(str(e))
        entry.pause()
        return None
        
    print("Saved to {!r}".format(fname))
    entry.pause()
    return fname
    
    
def load_db(default: str) -> Tuple[FlexibleStore, str]:
    p = "Enter filename to load from"
    if default is not None:
        p += " (default: {!r})".format(default)
    p += ":"
    
    fname = entry.get(str, p, allow_blank=True)
    if fname == "":
        fname = default
    
    try:
        with open(fname, 'r') as fp:
            store_dict = json.load(fp)
    except Exception as e:
        print("Could not load from {!r}:".format(fname))
        print(str(e))
        entry.pause()
        return None, None
        
    try:
        store = FlexibleStore.from_dict(store_dict)
    except Exception as e:
        print("Store file is not valid:")
        print(str(e))
        entry.pause()
        return None, None
    
    entry.pause("Loaded {!r}".format(fname))
    return store, fname
    

def load_dataset(default: str) -> Tuple[dict, str]:
    p = "Enter filename to load from"
    if default is not None:
        p += " (default: {!r})".format(default)
    p += ":"
    
    fname = entry.get(str, p, allow_blank=True)
    if fname == "":
        fname = default
    
    try:
        with open(fname, 'r') as fp:
            dataset = json.load(fp)
    except Exception as e:
        print("Could not load from {!r}:".format(fname))
        print(str(e))
        entry.pause()
        return None, None
    
    entry.pause("Loaded {!r}".format(fname))
    return dataset, fname
    
    
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
    ]
    
    tag_forms = parent_form.add_polymorphic_object_field(field_name, types, multivalue=multivalue, nullable=nullable)
    
    appearance_changed_form = tag_forms[0]
    appearance_changed_form.add_field("recipient")
    appearance_changed_form.add_field("appearance")
    
    state_changed_form = tag_forms[1]
    state_changed_form.add_field("recipient")
    state_changed_form.add_field("property")
    state_changed_form.add_field("value")
    
    char_obtains_item_form = tag_forms[2]
    char_obtains_item_form.add_field("character")
    char_obtains_item_form.add_field("item")
    
    char_drops_item_form = tag_forms[3]
    char_drops_item_form.add_field("character")
    char_drops_item_form.add_field("item")
    
    char_uses_item_form = tag_forms[4]
    char_uses_item_form.add_field("character")
    char_uses_item_form.add_field("item")
    char_uses_item_form.add_field("consumed", type=bool)
    
    char_gives_item_form = tag_forms[5]
    char_gives_item_form.add_field("giver")
    char_gives_item_form.add_field("receiver")
    char_gives_item_form.add_field("item")
    
    char_dies_form = tag_forms[6]
    char_dies_form.add_field("character")
    
    char_born_form = tag_forms[7]
    char_born_form.add_field("character")
    
    char_resurrected_form = tag_forms[8]
    char_resurrected_form.add_field("character")
    
    char_ports_in_form = tag_forms[9]
    char_ports_in_form.add_field("character")
    char_ports_in_form.add_field("port_out_event", nullable=True)
    
    char_ports_out_form = tag_forms[10]
    char_ports_out_form.add_field("character")
    char_ports_out_form.add_field("port_in_event", nullable=True)
    
    char_enters_form = tag_forms[11]
    char_enters_form.add_field("character")
    
    char_exits_form = tag_forms[12]
    char_exits_form.add_field("character")
    
    char_falls_asleep_form = tag_forms[13]
    char_falls_asleep_form.add_field("character")
    
    char_wakes_up_form = tag_forms[14]
    char_wakes_up_form.add_field("character")
    
    
def create_citation_field(parent_form, field_name, multivalue=False, nullable=False):
    types = ["dialog", "narration", "media", "commentary"]
    citation_forms = parent_form.add_polymorphic_object_field(field_name, types, multivalue=multivalue, nullable=nullable)
    cite_dialog_form, cite_narration_form, cite_media_form, cite_commentary_form = citation_forms
    cite_dialog_form.add_field("work")
    cite_dialog_form.add_field("panel", type=int)
    cite_dialog_form.add_field("line", type=int)
    cite_dialog_form.add_field("character")
    
    cite_narration_form.add_field("work")
    cite_narration_form.add_field("panel", type=int)
    cite_narration_form.add_field("paragraph", type=int)
    cite_narration_form.add_field("sentence", type=int)
    
    cite_media_form.add_field("work")
    cite_media_form.add_field("panel", type=int)
    cite_media_form.add_field("timestamp")
    
    cite_commentary_form.add_field("work")
    cite_commentary_form.add_field("volume", type=int)
    cite_commentary_form.add_field("page", type=int)
    

def create_constraint_field(parent_form, field_name, multivalue=False, nullable=False):
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
    immediate_form.add_field("ref_event")
    immediate_form.add_field("is_after", type=bool, default=True)
    
    jump_form = constraint_forms[1]
    jump_form.add_field("ref_event")
    jump_form.add_field("is_after", type=bool, default=True)
    
    entrypoint_form = constraint_forms[2]
    # there is no additional data
    
    narrative_causal_form = constraint_forms[3]
    narrative_causal_form.add_field("ref_event")
    narrative_causal_form.add_field("is_after", type=bool, default=True)
    
    abs_form = constraint_forms[4]
    abs_form.add_field("time")
    create_citation_field(abs_form, "citation", nullable=False)
    
    relative_form = constraint_forms[5]
    relative_form.add_field("ref_event")
    relative_form.add_field("is_after", type=bool, default=True)
    relative_form.add_field("distance")
    create_citation_field(relative_form, "citation", nullable=False)
    
    causal_form = constraint_forms[6]
    causal_form.add_field("time")
    create_citation_field(causal_form, "citation", nullable=False)
    
    sync_form = constraint_forms[7]
    sync_form.add_field("ref_event")
    create_citation_field(sync_form, "citation", nullable=False)
    
def enter_data() -> list[dict]:
    """
    Return a list of the event points entered.
    """
    
    form = Form()
    
    event_form = form.add_object_field("events", multivalue=True)
    
    event_form.add_auto_uuid_field("id")
    event_form.add_field("name")
    event_form.add_field("description")
    create_citation_field(event_form, "citations", multivalue=True)
    create_citation_field(event_form, "portrayed_in", nullable=True)
    create_event_tag_field(event_form, "tags", multivalue=True)
    create_constraint_field(event_form, "constraints", multivalue=True)
    
    univ_form = event_form.add_object_field("universes", multivalue=True)
    univ_form.add_field("name")
    univ_form.add_field("timeline")
    univ_form.add_field("location")
    univ_form.add_field("characters", multivalue=True)
    univ_form.add_field("items", multivalue=True)
    
    data = form.fill()
    
    return data['events']
    
