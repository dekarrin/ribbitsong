from .version import Version
from . import entry
from .store import FlexibleStore
from typing import Tuple, Optional

import json


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
            entry.pause("Not yet ready")
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
