from music21 import note, stream,scale,key
import os
   
import tensorflow as tf
import note_seq

from note_seq import midi_io,plot_sequence,play_sequence
import pyflp
import pandas as pd
from dict import *

def data_extraction_from_flp(file):
    '''
    Input: file path
    Output: 
        pattern_dfs : a dict that has the pattern name as key and a dataframe as value. The dataframe has the following columns:
            - Position: the start position of the note
            - End Position: the end position of the note
            - Key: the key of the note
            - Instrument: the name of the instrument
        trackz: a list of tuples where each tuple has the position and the name of the pattern in the whole music
    '''
    try :
        project = pyflp.parse(file)

        channels = {}
        for channel in project.channels:
            if type(channel) == pyflp.channel.Sampler:
                channels[channel.iid] = channel.name
            else:
                channels[channel.iid] = channel.name
                
        pattern_dfs = {}

        for pattern in project.patterns:
            for note in pattern.notes:
                instrument = pattern.name
                if instrument not in pattern_dfs:
                    pattern_dfs[instrument] = pd.DataFrame(columns=['Position', 'End Position', 'Key', 'Instrument'])
                note_dict = {
                    'Position': 16*note.position/(project.ppq),
                    'End Position': 16*note.position/(project.ppq) + 16*note.length/(project.ppq),
                    'Key': note.key,
                    'Instrument': channels[note.rack_channel]
                }

                pattern_dfs[instrument].loc[len(pattern_dfs[instrument])] = note_dict
        trackz =  []
        for arr in project.arrangements:
            for track in arr.tracks:
                if len(track) > 0:
                    for item in track:
                        if type(item) == pyflp.arrangement.PatternPLItem:
                            trackz.append((item.position, item.pattern.name))
        return pattern_dfs, trackz
    except Exception as e:
        print('np')
        return None, None


import pyflp
import pandas as pd




def data_extraction_from_flp_po(file):
    '''
    Input: file path
    Output: 
        pattern_dfs : a dict that has the pattern name as key and a dataframe as value. The dataframe has the following columns:
            - Position: the start position of the note
            - End Position: the end position of the note
            - Key: the key of the note
            - Instrument: the name of the instrument
        trackz: a list of tuples where each tuple has the position and the name of the pattern in the whole music
    '''
    try :
        
        return pyflp.parse(file)
    except Exception as e:
        print('NP',file)
        return None, None



def parcourir_dossier(dossier):
    tracks = {}

    for root, dirs, files in os.walk(dossier):
        for file in files:
            chemin_fichier = os.path.join(root, file)
            tracks[chemin_fichier.split('/')[-1]]= data_extraction_from_flp(chemin_fichier)
    return tracks

def parcourir_dossier_po(dossier,nb_files):
    tracks = {}
    files = []
    for root, dirs, files in os.walk(dossier):
        for i,file in enumerate(files):
            if i < nb_files:
                chemin_fichier = os.path.join(root, file)
                tracks[chemin_fichier.split('/')[-1]]= data_extraction_from_flp_po(chemin_fichier)
                files.append(chemin_fichier)
    return tracks,files

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

def find_file(folder_path, file_name):
    for root, dirs, files in os.walk(folder_path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

def display_pitches_for_key_mode(tonic, mode):
    """
    Display the pitches of a particular key and mode using music21.
    
    Parameters:
        tonic (str): The tonic note of the key (e.g., 'C', 'D#', etc.).
        mode (str): The mode of the scale (e.g., 'major', 'minor', 'dorian', etc.).
    """
    if mode == 'major':
        k = key.Key(tonic + 'M')
        scale_obj = scale.MajorScale(tonic)
    elif mode == 'minor':
        k = key.Key(tonic + 'm')
        scale_obj = scale.MinorScale(tonic)
    else:
        scale_obj = scale.ConcreteScale()
        scale_obj.tonic = tonic
        scale_obj.type = mode
        
    pitches = scale_obj.getPitches()
    return pitches  
  
def empty_note_sequence(qpm=120, total_time=0.0):
    note_sequence = note_seq.protobuf.music_pb2.NoteSequence()
    note_sequence.tempos.add().qpm = qpm
    note_sequence.ticks_per_quarter = note_seq.constants.STANDARD_PPQ
    note_sequence.total_time = total_time
    return note_sequence

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
    try :
        for mix in project.mixer:
            mixers[mix.iid] = mix.name
    except:
        nji = 0
    for channel in project.channels:
        try :
            channel_names[channel.iid] = (channel.name,mixers[channel.insert])
        except:
            channel_names[channel.iid] = (channel.name,channel.name)
            
    mapping = {}
    for key in channel_names:
        map_name = closest_midi_match(channel_names[key][0],midi_map)
        if map_name != "nothing":
            mapping[channel_names[key][0]] = map_name
        else:
            mapping[channel_names[key][0]] = closest_midi_match(channel_names[key][1],midi_map)
    return mapping

def fix_seq(found_file,tempo,limit):
    from music21 import note, stream,scale,key

    _, midi_data, _ = predict(found_file)

    note_sequence = midi_io.midi_to_note_sequence(midi_data)

    midi_sequence = []
    for notei in note_sequence.notes:
        midi_sequence.append(notei.pitch)
        
    # Créer un flux et ajouter les notes
    melody = stream.Stream()
    for midi_pitch in midi_sequence:
        melody.append(note.Note(midi_pitch))

    # Utiliser la fonction d'analyse de tonalité
    try:
        detected_key = melody.analyze('key')
        allowed = []
        for pitch in display_pitches_for_key_mode(detected_key.tonic.name, detected_key.mode):
            allowed.append(pitch.midi//12)
    except:
        allowed = [i for i in range(12)]




    note_sequence_new = empty_note_sequence()

    for notei in note_sequence.notes:
        if notei.end_time < limit and notei.pitch//12 in allowed:
            note_new = note_sequence_new.notes.add()
            note_new.start_time = int(notei.start_time*4*tempo/60)/(4*tempo/60)
            note_new.end_time = int(notei.end_time*4*tempo/60)/(4*tempo/60)
            note_new.pitch = notei.pitch
            note_new.instrument = notei.instrument
            note_new.program = notei.program
            note_new.velocity = notei.velocity
            note_new.is_drum = notei.is_drum
        
        
    return note_sequence_new

def is_percussion(name):
    for perc in beatmaking_percussion:
        if perc in name:
            return True
        
    if name in beatmaking_percussion:
        return True
    
    return False

