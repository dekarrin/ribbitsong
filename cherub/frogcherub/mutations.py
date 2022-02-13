import json

import yaql
from yaql.language.exceptions import YaqlLexicalException, YaqlGrammarException

def custom(dataset) -> int:
    engine = yaql.factory.YaqlFactory().create()
    running = True
    print("Custom data mutation mode.")
    print("Enter selection YAQL query, then enter mutation expression to be applied to")
    print("each. ")
    print("(type \q to quit)")
    while running:
        query = input("select> ")
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
        
        mutation = input("MUTATE> ")
        if mutation == r'\q':
            running = False
            continue
        print(type(result))
        

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
    