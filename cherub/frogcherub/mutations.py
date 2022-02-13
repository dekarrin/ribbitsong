import json
import re

import yaql
from yaql.language.exceptions import YaqlLexicalException, YaqlGrammarException

import jsonpath_ng
from jsonpath_ng.exceptions import JsonPathParserError

_ansi_escape_re = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def custom(dataset) -> int:
    total_updated = 0
    running = True
    print("Custom data mutation mode.")
    print()
    print("Enter selection JSONPath query, then enter mutation lambda to be applied to")
    print("each. For mutation lambdas, '_' is the original value.")
    print("(type \q to quit, \c to cancel mutation)")
    while running:
        query = input("select> ")
        query = _ansi_escape_re.sub('', query)
        if query == r'\q':
            running = False
            continue
        elif query == r'\c':
            continue
        
        try:
            expr = jsonpath_ng.parse(query)
        except JsonPathParserError as e:
            print(str(e))
            continue
        except AttributeError:
            print("Could not parse query, try again")
            continue
            
        matches = expr.find(dataset)
        if len(matches) < 1:
            print("(no results)")
            continue
        
        results = [match.value for match in matches]
        output = json.dumps(results, indent=2, sort_keys=True)
        print(output)
        
        mutie = input("MUTATE> ")
        mutie = _ansi_escape_re.sub('', mutie)
        if query == r'\q':
            running = False
            continue
        elif query == r'\c':
            continue
            
        mutation_func_str = 'lambda _: ' + mutie
        mutation_func = eval(mutation_func_str)
        for m in matches:
            old_val = m.value
            new_val = mutation_func(old_val)
            print("NEW VAL: {!r}".format(new_val))
            dataset = m.full_path.update(dataset, new_val)
            
        # show user the result by selecting the updated data once more
        updated_matches = expr.find(dataset)
        if len(updated_matches) < 1:
            raise ValueError("updated_matches somehow resulted in no results")
        updated_results = [m.value for m in updated_matches]
        updated_output = json.dumps(updated_results, indent=2, sort_keys=True)
        print(output)
           
        print("{!r} row(s) updated with mutation lambda".format(len(matches)))
        total_updated += len(matches)
    return total_updated
        

def universe_collapse(dataset) -> int:
    modified_count = 0
    
    for event in dataset['events']:
        univs = event['universes']
        new_univs = {}
        
        for u in univs:
            if 'characters' in u:
                needs_updating = True
                break
                
        if needs_updating:
            for u in univs:
                if 'characters' in u:
                    if u['name'] not in new_univs:
                        new_univs[u['name']] = {
                            "name": u['name'],
                            "timelines": {}
                        }    
                    new_univ = new_univs[u['name']]
                    
                    if u['timeline'] not in new_univ['timelines']:
                        new_univ['timelines'][u['timeline']] = {
                            "path": u['timeline'],
                            "locations": {}
                        }
                    new_tl = new_univ['timelines'][u['timeline']]
                    
                    if u['location'] not in new_tl['locations']:
                        new_tl['locations'][u['location']] = {
                            "path": u['location'],
                            "characters": [],
                            "items": []
                        }
                    new_loc = new_tl['locations'][u['location']]
                    
                    for ch in u['characters']:
                        if ch not in new_loc['characters']:
                            new_loc['characters'].append(ch)
                            
                    for item in u['items']:
                        if item not in new_loc['items']:
                            new_loc['items'].append(item)
                            
                        
                else:
                    if u['name'] not in new_univs:
                        new_univs[u['name']] = {
                            "name": u['name'],
                            "timelines": {}
                        }    
                    new_univ = new_univs[u['name']]
                    
                    for tl in u['timelines']:
                        if tl['path'] not in new_univ['timelines']:
                            new_univ['timelines'][tl['path']] = {
                                "path": tl['path'],
                                "locations": {}
                            }
                        new_tl = new_univ['timelines'][tl['path']]
                        
                        for loc in tl['locations']:
                            if loc['path'] not in new_tl['locations']:
                                new_tl['locations'][loc['path']] = {
                                    "path": loc['path'],
                                    "characters": [],
                                    "items": []
                                }
                            new_loc = new_tl['locations'][loc['path']]
                            
                            for ch in loc['characters']:
                                if ch not in new_loc['characters']:
                                    new_loc['characters'].append(ch)
                                    
                            for item in loc['items']:
                                if item not in new_loc['items']:
                                    new_loc['items'].append(item)
            
            # now convert it into actual proper format
            formatted_new_univs = []
            for u_name in new_univs:
                u = new_univs[u_name]
                formatted_univ = {
                    "name": u_name,
                    "timelines": []
                }
                for tl_path in u['timelines']:
                    tl = u['timelines'][tl_path]
                    formatted_tl = {
                        "path": tl_path,
                        "locations": []
                    }
                    for loc_path in tl['locations']:
                        loc = tl['locations'][loc_path]
                        formatted_tl['locations'].append(loc)
                    formatted_univ['timelines'].append(formatted_tl)
                formatted_new_univs.append(formatted_univ)
                
            # and assign it
            event['universes'] = formatted_new_univs
            modified_count += 1
    return modified_count
    