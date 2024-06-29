
from tqdm import tqdm
from implementations import *



def tracks_to_events(tracks,begin_bar=0,end_bar=20,tdelta=4):
    verses = {}
    choruses = {}
    file_note_seqs = {}
    percses = {}
    not_Working = []
    iid_to_name = {}
    for idx,project in tqdm(enumerate(tracks)):
            if True:
                verse = {}
                patterns = {}
                #percs = []
                pattern_all = {}
                try:
                    channels_map = map_channel_wmm(tracks[project])
                    channels = {}
                    for channel in tracks[project].channels:
                        channels[channel.iid] = channel.name
                    for pattern in tracks[project].patterns:
                        pattern_all[pattern.iid] = pattern
                        for note in pattern.notes:
                            ch = note.rack_channel
                            break
                        if pattern.name not in patterns:
                    
                            patterns[pattern.iid] = channels_map[channels[ch]]
                            iid_to_name[pattern.iid] = pattern.name
                                                            
                    tr = []
                    for arrangement in tracks[project].arrangements:
                        for (track) in arrangement.tracks:
                            if len(track) != 0:
                                for item in track:
                                        if type(item) == pyflp.arrangement.PatternPLItem:
                                            tr.append((item.position,  patterns[item.pattern.iid],item.pattern.iid,True,item.offsets,item.length))
                                        
                    tr = sorted(tr, key=lambda x: x[0])
                    prev = 0
                    for i in tr:
                        first = True
                        if i[0] < end_bar * 4*tracks[project].ppq :
                            if i[3]:
                                    if str(i[4][0]) == 'nan' or int(i[4][0]) == 0:
                                        for note in (pattern_all[i[2]]).notes:
                                            if note.position < i[5]:

                                                npos = note.position + i[0] 
                                                if round(tdelta*(npos + note.length)/tracks[project].ppq) <= end_bar * 16 and int(tdelta*(npos)/tracks[project].ppq) >= begin_bar*16 and round(tdelta*npos/tracks[project].ppq) != round((tdelta*(npos + note.length))/tracks[project].ppq):                                               
                                                        if not is_percussion(i[1].lower()):
                                                            if first:
                                                                for num_inst in range(10):
                                                                    if f'{i[1]}_{str(num_inst)}' not in verse:
                                                                        verse[f'{i[1]}_{str(num_inst)}'] = []
                                                                        break
                                                                first = False
                                                            verse[f'{i[1]}_{str(num_inst)}'].append({'type' : 'NOTE_ON',  'keys':note.key,  'delta':round((tdelta*npos-begin_bar*16*tracks[project].ppq)/tracks[project].ppq)})
                                                            verse[f'{i[1]}_{str(num_inst)}'].append({'type' : 'NOTE_OFF', 'keys': note.key, 'delta': round(((tdelta*(npos + note.length)-begin_bar*16*tracks[project].ppq))/tracks[project].ppq)})
                    
                                    else:     
                                        for note in (pattern_all[i[2]]).notes:
                                            if note.position*Q_BAR_OFFSET >= i[4][0] and note.position - int(i[4][0]/Q_BAR_OFFSET)  < i[5]:
                                                npos = note.position - int(i[4][0]/Q_BAR_OFFSET) + i[0] 
                                                if round(tdelta*(npos + note.length)/tracks[project].ppq) <= end_bar * 16 and int(tdelta*(npos)/tracks[project].ppq) >= begin_bar*16 and round(tdelta*npos/tracks[project].ppq) != round((tdelta*(npos + note.length))/tracks[project].ppq):                                               
                                                        if not is_percussion(i[1].lower()):
                                                            if first:
                                                                for num_inst in range(10):
                                                                    if f'{i[1]}_{str(num_inst)}' not in verse:
                                                                        verse[f'{i[1]}_{str(num_inst)}'] = []
                                                                        break
                                                                first = False
                                                            verse[f'{i[1]}_{str(num_inst)}'].append({'type' : 'NOTE_ON',  'keys':note.key,  'delta':round((tdelta*npos-begin_bar*16*tracks[project].ppq)/tracks[project].ppq)})
                                                            verse[f'{i[1]}_{str(num_inst)}'].append({'type' : 'NOTE_OFF', 'keys': note.key, 'delta': round(((tdelta*(npos + note.length)-begin_bar*16*tracks[project].ppq))/tracks[project].ppq)})
                            
                                    
                    verses[project] = verse
                except Exception as e:
                    not_Working.append(project)
    return verses,percses,not_Working

def dict_to_txt(verses,percses,tracks,tdelta,with_bpm=False,instr=0):
    tts = []
    all = 0
    bars = []
    patt = 0
    patt_all = 0
    genre_dis = { styles[style] : 0 for style in styles}
    genre_dis['OTHER'] = 0
    objects = {}
    for pattern_dfs in tqdm(verses):
        times = []
        patt_all += 1
        if len(verses[pattern_dfs]) != 0:
                patt += 1   
                timel = [0]
                time0l = [1000]
                if with_bpm:
                    if pattern_dfs.split('_')[0] not in styles:
                        string = 'PIECE_START' + ' GENRE=OTHER BPM=' + str(int(tracks[pattern_dfs].tempo)) + ' '
                        genre_dis['OTHER'] += 1
                    else:
                        string = 'PIECE_START' + ' GENRE='+ (styles[pattern_dfs.split('_')[0]].upper()).replace(' ','') +  ' BPM=' + str(int(tracks[pattern_dfs].tempo)) + ' '
                        genre_dis[styles[pattern_dfs.split('_')[0]]] += 1
                else:  
                    if pattern_dfs.split('_')[0] not in styles:
                        string = 'PIECE_START' + ' GENRE=OTHER '
                        genre_dis['OTHER'] += 1
                    else:
                        string = 'PIECE_START' + ' GENRE='+ (styles[pattern_dfs.split('_')[0]].upper()).replace(' ','') + ' '
                        genre_dis[styles[pattern_dfs.split('_')[0]]] += 1 
                    
                num_tracks = 0
                for pattern in verses[pattern_dfs]:
                    bar_string = ' '
                    all += 1
                   
                    if closest_midi_match(pattern,midi_map).title() != 'Nothing':
                        if type(full_midi_dict[instrument_dict[closest_midi_match(pattern,midi_map).title()]]) != tuple:
                            bar = 0
                            num_tracks += 1
                            bar_string += 'TRACK_START INST=' + str(full_midi_dict[instrument_dict[closest_midi_match(pattern,midi_map).title()]]) + ' BAR_START '
                            pattern_2 = sorted(verses[pattern_dfs][pattern],key = lambda x: x['delta'])
                            time0l.append(pattern_2[0]['delta'])
                            time = 0
                            current_notes= []
                            for idx,note in enumerate(pattern_2):
                                if note['delta']//(4*tdelta) > 8 :
                                    print('tkharbi9')
                                if note['delta']//(4*tdelta) > bar :
                                    for i in range(min(note['delta']//(4*tdelta),7) - bar):
                                        bar_string += 'BAR_END BAR_START '
                                    bar = min(note['delta']//(4*tdelta),7)
                                    time = max((4*tdelta)*bar,time)
                                    
                                    
                                delta = note['delta'] - time
                                if delta > 16:
                                    print(note['delta'],time,bar)
                                if type(note['keys']) == int:
                                    bar_string += 'TIME_DELTA=' + str(delta) + ' ' + note['type'] + '=' + str(note['keys']) + ' ' 
                                else:
                                    bar_string += 'TIME_DELTA=' + str(delta) + ' ' + note['type'] + '=' + str(midi_note_dict[note['keys']]) + ' ' 
        
                                time = note['delta']
                            timel.append(time)
                            bars.append(bar)
                            

                            bar_string += 'BAR_END TRACK_END '    
                    else:
                        bar_string += 'TRACK_START INST=1 BAR_START '
                        bar = 0
                        time = 0

                        num_tracks += 1
                        pattern_2 = sorted(verses[pattern_dfs][pattern],key = lambda x: x['delta'])
                        time0l.append(pattern_2[0]['delta'])

                        for note in pattern_2:
                            if note['delta']//(4*tdelta) > 8 :
                                    print('tkharbi9')
                            if note['delta']//(4*tdelta) > bar :
                                
                                for i in range(min(note['delta']//(4*tdelta),7) - bar):
                                    bar_string += 'BAR_END BAR_START '
                                bar = min(note['delta']//(4*tdelta),7)
                                time = max((4*tdelta)*bar,time)
                            delta = note['delta'] - time
                    
                            if type(note['keys']) == int:
                                bar_string += 'TIME_DELTA=' + str(delta) + ' ' + note['type'] + '=' + str(note['keys']) + ' ' 
                            else:
                                bar_string += 'TIME_DELTA=' + str(delta) + ' ' + note['type'] + '=' + str(midi_note_dict[note['keys']]) + ' ' 
              
                            time = note['delta']
                        timel.append(time)
                        bars.append(bar)

                        bar_string += 'BAR_END TRACK_END ' 

                    # if time > 120 and time0 < 8:
                    #    string += bar_string 
                    string += bar_string 
                string += 'PIECE_END'
                tts.append(times)
                if min(time0l) < 8 and max(timel) > 120:
                    objects[pattern_dfs] = string
                # else:
                #     objects[pattern_dfs] = string

    return objects, genre_dis,instr


                
def extract_folder_to_txt_for_chunks(tracks,dest_folder,begin_bar,end_bar,nbf,tdelta,with_bpm=False,instr=set()):
    
    print('Converting to events')

    verses,percses,not_Working = tracks_to_events(tracks,begin_bar,end_bar,tdelta)
    print('Converted to events')
    print('Converting to txt')
    
    objects, genre_dis,instr = dict_to_txt(verses,percses,tracks,tdelta,with_bpm,instr)
    return objects, genre_dis,instr

def extract_folder_to_txt(folder,dest_folder,begin_bar,end_bar,nbf,tdelta,with_bpm=False):
    print('Extracting')

    tracks,files = parcourir_dossier_po(folder,nbf)
    print('Extracted')
    print('Converting to events')

    verses,percses,not_Working = tracks_to_events(tracks,begin_bar,end_bar,tdelta)
    print('Converted to events')
    print('Converting to txt')
    
    objects,genre_dis,instr = dict_to_txt(verses,percses,tracks,tdelta,with_bpm)
    for f in objects:
            with open(f"{dest_folder}/{f.replace('.flp','.txt')}", "w") as file:
                        # Write the string to the file
                        file.write(objects[f])
    return objects, genre_dis

def chunks_division(folder,dest_folder,size_bar,nbf,tdelta,with_bpm=False,chunks_per_music=1):
    tracks,files = parcourir_dossier_po(folder,nbf)

    instr = set()
    for ch in range(30):
        objects, genre_dis ,instr= extract_folder_to_txt_for_chunks(tracks,dest_folder,ch*2,(ch*2)+size_bar,nbf,tdelta,with_bpm,instr)
        for f in objects:
            with open(f"{dest_folder}/{f.replace('.flp','.txt')}-{ch}", "w") as file:
                        # Write the string to the file
                        file.write(objects[f])
    
def extract_file_to_txt(file,dest_folder,begin_bar,end_bar,nbf,tdelta,with_bpm=False):
    print('Extracting')
    tracks = {}
    tracks[file.split('/')[-1]] = pyflp.parse(file)
    print('Extracted')
    print('Converting to events')

    verses,percses,not_Working = tracks_to_events(tracks,begin_bar,end_bar,tdelta)
    print('Converted to events')
    print('Converting to txt')
    
    objects,genre_dis,instr = dict_to_txt(verses,percses,tracks,tdelta,with_bpm)
    for f in objects:
            with open(f"{dest_folder}/{f.replace('.flp','.txt')}", "w") as file:
                        # Write the string to the file
                        file.write(objects[f])
    return objects, genre_dis