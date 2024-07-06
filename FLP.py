
from tqdm import tqdm
from implementations import *
from collections import defaultdict
import random
import pyflp
from display import token_sequence_to_note_sequence
import note_seq
import os

class FLP_handler:
    def __init__(self,flp_file,time_delta):
        self.flp_file = flp_file
        self.error = self.error_check()
        if self.error:
            self.ppq = None
            self.time_delta = None
            self.genre = styles[flp_file.split('/')[-1].split('_')[0]].upper().replace(' ','') if flp_file.split('/')[-1].split('_')[0] in styles else 'OTHER'
            self.track_info, self.iid_to_pattern , self.pattern_iid_to_inst, \
                self.pattern_iid_to_name , self.channels__iid_to_inst , \
                        self.channel_iid_to_name = None, None, None, None, None, None
            self.notes = None
            self.composition = None
        else:
            self.ppq = self.project.ppq
            self.time_delta = time_delta
            self.genre = styles[flp_file.split('/')[-1].split('_')[0]].upper().replace(' ','') if flp_file.split('/')[-1].split('_')[0] in styles else 'OTHER'
            self.track_info, self.iid_to_pattern , self.pattern_iid_to_inst, \
                    self.pattern_iid_to_name , self.channels__iid_to_inst , \
                            self.channel_iid_to_name = self.list_patterns()
            self.notes = self.list_notes(self.track_info)
            self.composition = self.to_composition(self.notes)
    
    def error_check(self):
        unreadable = False
        try:
            self.project = pyflp.parse(self.flp_file)
        except:
            unreadable = True
        
        try:
            for channel in self.project.channels:
                nothing = 0
        except:
            unreadable = True
            
        try:
            for arrangements in self.project.arrangements:
                for track in arrangements.tracks:
                    nothing = 0
        except:
            unreadable = True
        
        return unreadable
            
        
    def list_patterns(self):
        track_info = {}
        iid_to_pattern = {}
        pattern_iid_to_inst = {}
        pattern_iid_to_name = {}
        channels__iid_to_inst = map_channel_wmm(self.project)
        self.instrument_mapping = channels__iid_to_inst
        channel_iid_to_name = {}
        
        for channel in self.project.channels:
            channel_iid_to_name[channel.iid] = channel.name
            
        for pattern in self.project.patterns:
            iid_to_pattern[pattern.iid] = pattern
            for note in pattern.notes:
                ch = note.rack_channel
                break
            pattern_iid_to_inst[pattern.iid] = channels__iid_to_inst[ch]
            pattern_iid_to_name[pattern.iid] = pattern.name

        tr_number = 0                              
        for arrangement in self.project.arrangements:
            for track in arrangement.tracks:
                if len(track) != 0:
                    tr_number += 1
                    for item in track:
                            if type(item) == pyflp.arrangement.PatternPLItem:
                                key = (tr_number,pattern_iid_to_inst[item.pattern.iid])
                                if key not in track_info:
                                    track_info[key] = []
                                track_info[key].append({'position' : item.position,  
                                                        'instrument' : pattern_iid_to_inst[item.pattern.iid],
                                                        'offsets': item.offsets,
                                                        'length' :item.length,
                                                        'pattern_object' :iid_to_pattern[item.pattern.iid] }) #group by (track, instrument)
        return track_info, iid_to_pattern , pattern_iid_to_inst,  pattern_iid_to_name , channels__iid_to_inst , channel_iid_to_name
        
    def list_notes(self,track_info):
        track_final = [] 

        for key in track_info:
            if not is_percussion(key[1].lower()):
                current_track = []      
                for item in track_info[key]:
                    for note in item['pattern_object'].notes: #iterate over notes
                            if type(note.key) != int :
                                pitch = str(midi_note_dict[note.key])
                            else:
                                pitch = str(note.key)
                                
                            if str(item['offsets'][0]) == 'nan' or item['offsets'][0] == 0:   #check if there is an offset
                                if note.position < item['length']:
                                    note_position = note.position + item['position'] 
                                    if round(self.time_delta*note_position/self.ppq) != round(self.time_delta*(note_position + note.length)/self.ppq):
                                        current_track.append({'message_type' : 'NOTE_ON',  
                                                                'pitch':pitch,  
                                                                'position':note_position})
                                        
                                        current_track.append({'message_type' : 'NOTE_OFF', 
                                                                'pitch': pitch, 
                                                                'position': note_position + note.length})
                            else:     
                                if note.position*Q_BAR_OFFSET >= item['offsets'][0] and \
                                                            note.position - int(item['offsets'][0]/Q_BAR_OFFSET)  < item['length']:
                                    note_position = note.position - int(item['offsets'][0]/Q_BAR_OFFSET) + item['position']
                                    if round(self.time_delta*note_position/self.ppq) != round(self.time_delta*(note_position + note.length)/self.ppq):
                                        current_track.append({'message_type' : 'NOTE_ON',  
                                                                'pitch':pitch,  
                                                                'position':note_position})
                                        
                                        current_track.append({'message_type' : 'NOTE_OFF', 
                                                                'pitch': pitch, 
                                                                'position': note_position + note.length})
                                    
                                    
                track_final.append((key[1],current_track))

        return track_final

    def pick_random_instrument(self):
        instrument_id = str(random.randint(1, 8))
        return instrument_id

    def to_composition(self,track_final):
        
        composition = {'genre': self.genre, 'bpm': 0, 'tracks': []}
        for element in track_final:
            if element[0].title() == 'Nothing':
                instrument_id = self.pick_random_instrument()
            else:
                instrument_id = str(full_midi_dict[instrument_dict[element[0].title()]])
                
            composition['tracks'].append({'instrument': instrument_id,'bars' : defaultdict(list) })
            messages = sorted(element[1],key = lambda x: x['position'])
            for message in messages:
                message_position = round(self.time_delta*message['position']/self.ppq)
                if message['message_type'] == 'NOTE_OFF' and message_position/16 == message_position//16:
                    bar = message_position//16 - 1
                else:
                    bar = message_position//16
                    
                composition['tracks'][-1]['bars'][bar].append({'type': message['message_type'], 'pitch': message['pitch'], 'position': message_position})
                    
        return composition

    def is_empty(self,track,begin_bar,end_bar):
        is_empty = True
        for bar in range(begin_bar-1,end_bar):
            if len(track['bars'][bar]) > 0:
                is_empty = False
                break
        return is_empty
    
    def to_textual(self,composition,begin_bar,end_bar):
        string = f"PIECE_START GENRE={composition['genre']} "
        beggining_control = 10000
        end_control = 10000
        for track in composition['tracks']:
            if not self.is_empty(track,begin_bar,end_bar):
                string += f"TRACK_START INST={str(track['instrument'])} "
                for bar in range(begin_bar-1,end_bar):
                    if not self.is_empty(track,bar,end_bar):
                        current_time = bar*16
                        string += 'BAR_START '
                        if bar in track['bars']:
                            for note in track['bars'][bar]:
                                if beggining_control == 10000:
                                    beggining_control = note['position'] - 16*begin_bar
                                time_delta = note['position'] - current_time
                                if time_delta > 0:
                                    string += f'TIME_DELTA={time_delta} '
                                string += f"{note['type']}={str(note['pitch'])} "
                                current_time = note['position']
                        string += 'BAR_END '
                string += 'TRACK_END '
                end_control =  16*end_bar - current_time 
        string += 'PIECE_END'
        return string,beggining_control, end_control
    
    def to_note_sequence(self,begin_bar,end_bar,nth):
        if nth is None:
            note_sequence = token_sequence_to_note_sequence(self.to_textual(self.composition,begin_bar,end_bar)[0],(1/(self.time_delta)) * 60/120, BAR_LENGTH_120BPM = self.time_delta* 60 / 120)
        else:
            text = self.to_textual(self.composition,begin_bar,end_bar)[0]
            if len(text.split('TRACK_START')) > nth+1:
                text = 'TRACK_START' + text.split('TRACK_START')[nth+1]
                note_sequence = token_sequence_to_note_sequence(text,(1/(self.time_delta)) * 60/120, BAR_LENGTH_120BPM = self.time_delta* 60 / 120)

            else:
                print('Track not found')

                return None
                
        return note_sequence
        
    def plotandplay(self,begin_bar,end_bar,nth=None):
        note_sequence = self.to_note_sequence(begin_bar,end_bar,nth)
        if note_sequence is not None:
            note_seq.plot_sequence(note_sequence)
            note_seq.play_sequence(note_sequence)  
 

    def get_composition(self):
        return self.composition
    
    def get_textual(self,begin_bar,end_bar):
        return self.to_textual(self.composition,begin_bar,end_bar)
    
    def get_notes(self):
        return self.notes
    
    def get_project(self):
        return self.project
    
    def get_track_info(self):
        return self.track_info
    
    def get_project(self):
        return self.project
    
    def get_composition(self):
        return self.composition
    

    
    def get_notes(self):
        return self.notes
    
    def get_project(self):
        return self.project
    
    def get_track_info(self):
        return self.track_info
    
    
class FLP_Dataset:
    def __init__(self,):
        self.dataset = []
        self.flp_handlers = []
    
    def parse_flp_files(self,folder):
        flp_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.flp')]
        errors = 0
        flp_files = flp_files[:self.nb_files]
        flp_handlers = []
        for flp_file in tqdm(flp_files):
            handler = FLP_handler(flp_file,self.time_delta)
            if handler.error_check():
                errors += 1
                #print(f'Error while parsing {flp_file}')
            else:
                flp_handlers.append(handler)
            
        return flp_handlers, errors/len(flp_files)
    
    def generate_dataset(self,folder, nb_files = 10, time_delta = 4, bar_size = 8, nb_chunks = 1, chunk_offset = 2, complete=True):
        self.time_delta = time_delta
        self.bar_size = bar_size
        self.nb_chunks = nb_chunks
        self.chunk_offset = chunk_offset
        self.nb_files = nb_files
        self.dataset = []
        flp_objects, error_rate = self.parse_flp_files(folder)
        for chunk in range(self.nb_chunks):
            for flp_object in flp_objects:
                generation = flp_object.get_textual(begin_bar = chunk*self.chunk_offset + 1, end_bar = chunk*self.chunk_offset + self.bar_size)
                if complete:
                    if generation[1] < self.time_delta/2 and generation[2] < self.time_delta/2:
                        self.dataset.append(generation[0])
                        self.flp_handlers.append(flp_object)
                else:
                    self.dataset.append(generation[0])
                    self.flp_handlers.append(flp_object)
                    
        return self.dataset, self.flp_handlers, error_rate
    
    def __getitem__(self, index):
        return self.dataset[index]
    def __len__(self):
        return len(self.dataset)