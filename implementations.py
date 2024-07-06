
import pandas as pd
from dict import *









def map_channel(project):
    channel_names = {}
    mixers = {}
    for mix in project.mixer:
        mixers[mix.iid] = mix.name
    for channel in project.channels:
        try :
            channel_names[channel.iid] = (channel.name,mixers[channel.insert])
        except:
            channel_names[channel.iid] = (channel.name,channel.name)
    return channel_names
def closest_midi_match(name, midi_map):
    # Initialize the result dictionary
    result = {}

    norm_midi_map = [el.strip().lower() for el in midi_map]
    if name == None:
        return "nothing"
    normalized_instrument = name.strip().lower()

    closest_match = None
    for key in norm_midi_map:
        if key in normalized_instrument:
            closest_match = key
     
            break

    # Add the match to the result dictionary
    if closest_match != None:
        return closest_match
    else:
        return "nothing"





def find_closest_midi_match(instrument_list, midi_map):
    # Initialize the result dictionary
    result = {}

    # Normalize the names for matching (lowercase and removing extra spaces)
    nones = 0
    norm_midi_map = [el.strip().lower() for el in midi_map]
    all = 0
    # Iterate through each item in the provided list
    for instrument in instrument_list:
        all += 1
        # Normalize the input instrument for matching
        normalized_instrument = instrument.strip().lower()
        # Attempt to find the closest match
        closest_match = None
        for key in norm_midi_map:
            if key in normalized_instrument:
                closest_match = key
                break
    
        # Add the match to the result dictionary
        if closest_match != None:
            result[instrument] = closest_match
        else:
            result[instrument] = "nothing"
            nones += 1
    return result

def map_channel_wmm(project):
    channel_names = {}
    mixers = {}
    try:
        for mix in project.mixer:
            mixers[mix.iid] = mix.name
    except:
        pass

    for channel in project.channels:
        try :
            channel_names[channel.iid] = (channel.name,mixers[channel.insert])
        except:
            channel_names[channel.iid] = (channel.name,channel.name)
            
    mapping = {}
    for key in channel_names:
        map_name = closest_midi_match(channel_names[key][0],midi_map)
        if map_name != "nothing":
            mapping[key] = map_name
        else:
            mapping[key] = closest_midi_match(channel_names[key][1],midi_map)
    return mapping





def is_percussion(name):
    for perc in beatmaking_percussion:
        if perc in name:
            return True
        
    if name in beatmaking_percussion:
        return True
    
    return False

