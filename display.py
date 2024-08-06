import note_seq
import re
import matplotlib.pyplot as plt


def token_sequence_to_note_sequence(token_sequence, use_program=True, use_drums=True, instrument_mapper=None, only_piano=False,NOTE_LENGTH_16TH_120BPM = 0.25 * 60 / 120, BAR_LENGTH_120BPM = 16.0 * 60 / 120):

    if isinstance(token_sequence, str):
        token_sequence = token_sequence.split()
    note_sequence = empty_note_sequence()

    # Render all notes.
    current_program = 1
    current_is_drum = False
    current_instrument = 0
    track_count = 0
    for token_index, token in enumerate(token_sequence):

        if token == "PIECE_START":
            pass
        elif token == "PIECE_END":
            print("The end.")
            break
        elif token == "TRACK_START":
            current_notes = {}
            current_bar_index = 0
            track_count += 1
            
            pass
        elif token == "TRACK_END":
            pass
        elif token == "KEYS_START":
            pass
        elif token == "KEYS_END":
            pass
        elif token.startswith("KEY="):
            pass
        elif token.startswith("INST"):
            instrument = token.split("=")[-1]
            if instrument != "DRUMS" and use_program:
                if instrument_mapper is not None:
                    if instrument in instrument_mapper:
                        instrument = instrument_mapper[instrument]
                current_program = int(instrument)
                current_instrument = track_count
                current_is_drum = False
            if instrument == "DRUMS" and use_drums:
                current_instrument = 0
                current_program = 0
                current_is_drum = True
        elif token == "BAR_START":
            current_time = current_bar_index * BAR_LENGTH_120BPM
        elif token == "BAR_END":
            current_bar_index += 1
            pass
        elif token.startswith("NOTE_ON"):
            pitch = int(token.split("=")[-1])
            note = note_sequence.notes.add()
            note.start_time = current_time
            note.end_time = current_time + 4 * NOTE_LENGTH_16TH_120BPM
            note.pitch = pitch
            note.instrument = current_instrument
            note.program = current_program
            note.velocity = 80
            note.is_drum = current_is_drum
            current_notes[pitch] = note
        elif token.startswith("NOTE_OFF"):
            pitch = int(token.split("=")[-1])
            if pitch in current_notes:
                note = current_notes[pitch]
                note.end_time = current_time

        elif token.startswith("TIME_DELTA"):
            delta = float(token.split("=")[-1]) * NOTE_LENGTH_16TH_120BPM
            current_time += delta
        elif token.startswith("DENSITY="):
            pass
        elif token == "[PAD]":
            pass
        else:
            #print(f"Ignored token {token}.")
            pass

    # Make the instruments right.
    instruments_drums = []
    for note in note_sequence.notes:
        pair = [note.program, note.is_drum]
        if pair not in instruments_drums:
            instruments_drums += [pair]
        note.instrument = instruments_drums.index(pair)

    if only_piano:
        for note in note_sequence.notes:
            if not note.is_drum:
                note.instrument = 0
                note.program = 0

    return note_sequence

def empty_note_sequence(qpm=120.0, total_time=0.0):
    note_sequence = note_seq.protobuf.music_pb2.NoteSequence()
    note_sequence.tempos.add().qpm = qpm
    note_sequence.ticks_per_quarter = note_seq.constants.STANDARD_PPQ
    note_sequence.total_time = total_time
    return note_sequence

import note_seq
import collections
import numpy as np
import pandas as pd
import bokeh.plotting
import bokeh.models
import bokeh.palettes

def plot_sequence(sequence, marker_times=None, show_figure=True):
    """Creates an interactive pianoroll for a NoteSequence.

    Example usage: plot a random melody.
        sequence = mm.Melody(np.random.randint(36, 72, 30)).to_sequence()
        bokeh_pianoroll(sequence)

    Args:
        sequence: A NoteSequence.
        marker_times: A list of float representing the times (in seconds) to place the markers.
        show_figure: A boolean indicating whether or not to show the figure.

    Returns:
        If show_figure is False, a Bokeh figure; otherwise None.
    """

    def _sequence_to_pandas_dataframe(sequence):
        """Generates a pandas dataframe from a sequence."""
        pd_dict = collections.defaultdict(list)
        for note in sequence.notes:
            pd_dict['start_time'].append(note.start_time)
            pd_dict['end_time'].append(note.end_time)
            pd_dict['duration'].append(note.end_time - note.start_time)
            pd_dict['pitch'].append(note.pitch)
            pd_dict['bottom'].append(note.pitch - 0.4)
            pd_dict['top'].append(note.pitch + 0.4)
            pd_dict['velocity'].append(note.velocity)
            pd_dict['fill_alpha'].append(note.velocity / 128.0)
            pd_dict['instrument'].append(note.instrument)
            pd_dict['program'].append(note.program)

        # If no velocity differences are found, set alpha to 1.0.
        if np.max(pd_dict['velocity']) == np.min(pd_dict['velocity']):
            pd_dict['fill_alpha'] = [1.0] * len(pd_dict['fill_alpha'])

        return pd.DataFrame(pd_dict)

    # These are hard-coded reasonable values, but the user can override them
    # by updating the figure if need be.
    fig = bokeh.plotting.figure(
        tools='hover,pan,box_zoom,reset,save')
    fig.width = 500
    fig.height = 200
    fig.xaxis.axis_label = 'time (sec)'
    fig.yaxis.axis_label = 'pitch (MIDI)'
    fig.yaxis.ticker = bokeh.models.SingleIntervalTicker(interval=12)
    fig.ygrid.ticker = bokeh.models.SingleIntervalTicker(interval=12)
    # Pick indexes that are maximally different in Spectral8 colormap.
    spectral_color_indexes = [7, 0, 6, 1, 5, 2, 3]

    # Create a Pandas dataframe and group it by instrument.
    dataframe = _sequence_to_pandas_dataframe(sequence)
    instruments = sorted(set(dataframe['instrument']))
    grouped_dataframe = dataframe.groupby('instrument')
    for counter, instrument in enumerate(instruments):
        instrument_df = grouped_dataframe.get_group(instrument)
        color_idx = spectral_color_indexes[counter % len(spectral_color_indexes)]
        color = bokeh.palettes.Spectral8[color_idx]
        source = bokeh.plotting.ColumnDataSource(instrument_df)
        fig.quad(top='top', bottom='bottom', left='start_time', right='end_time',
                 line_color='black', fill_color=color,
                 fill_alpha='fill_alpha', source=source)
    fig.select(dict(type=bokeh.models.HoverTool)).tooltips = (
        {'pitch': '@pitch',
         'program': '@program',
         'velo': '@velocity',
         'duration': '@duration',
         'start_time': '@start_time',
         'end_time': '@end_time',
         'velocity': '@velocity',
         'fill_alpha': '@fill_alpha'})

    # Add the marker lines if specified
    if marker_times is not None:
        for marker_time in marker_times:
            marker = bokeh.models.Span(location=marker_time, dimension='height', line_color='red', line_width=2)
            fig.add_layout(marker)

    if show_figure:
        bokeh.plotting.output_notebook()
        bokeh.plotting.show(fig)
        return None
    return fig


def display(file_path,tdelta,begin_bar,end_bar):
    try:
        with open(file_path, "r") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IOError:
        print(f"Error reading file '{file_path}'.")
    # Assuming 'content' is the string you want to search in
    pattern = r'BPM=(\d+)'
    match = re.search(pattern, content)

    if match:
        bpm = int(match.group(1))
   
    if len(content.split()) > 5:
        print(content)
        note_sequence_ch = token_sequence_to_note_sequence(content,NOTE_LENGTH_16TH_120BPM = (1/(tdelta)) * 60/120, BAR_LENGTH_120BPM = 4* 60 / 120)
        #note_seq.plot_sequence(note_sequence_ch,ax=ax)
        
        # Exemple d'utilisation
        marker_times = []
        for mark in range(end_bar-begin_bar+1):
            marker_times.append((mark+1) * 4 * 60 / 120)
        plot_sequence(note_sequence_ch, marker_times=marker_times)



        note_seq.play_sequence(note_sequence_ch) 
       
 
    else:
        print("No notes to display.")
    
    # if len(content.split()) > 13:
    #     for i in range(len(content.split('TRACK_START'))):
    #         if len(content.split('TRACK_START')[i].split()) > 15:
    #             print(len(content.split('TRACK_START')),i)
    #             note_sequence_ch = token_sequence_to_note_sequence('TRACK_START ' + content.split('TRACK_START')[i],NOTE_LENGTH_16TH_120BPM = (1/(tdelta)) * 60/bpm, BAR_LENGTH_120BPM = 16 * 60 / bpm)
    #             note_seq.plot_sequence(note_sequence_ch)
    #             note_seq.play_sequence(note_sequence_ch)  
    # else:
    #     print("No notes to display.")
    
def display_txt(content,tdelta,tempo):
    
    if len(content.split()) > 4:
        print(content)
        note_sequence_ch = token_sequence_to_note_sequence(content,NOTE_LENGTH_16TH_120BPM = (1/(tdelta)) * 60/tempo, BAR_LENGTH_120BPM = 4* 60 / tempo)
        #note_seq.plot_sequence(note_sequence_ch,ax=ax)
        
        # Exemple d'utilisation
        marker_times = []
        for mark in range(7):
            marker_times.append((mark+1) * 4 * 60 / tempo)
        plot_sequence(note_sequence_ch, marker_times=marker_times)



        note_seq.play_sequence(note_sequence_ch)   
       
 
    else:
        print("No notes to display.")
    
def display_line(file_path,tdelta,begin_bar,end_bar):
    try:
        with open(file_path, "r") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IOError:
        print(f"Error reading file '{file_path}'.")
    # Assuming 'content' is the string you want to search in
    pattern = r'BPM=(\d+)'
    match = re.search(pattern, content)

    if match:
        bpm = int(match.group(1))
   
    if len(content.split()) > 13:
        print(content)
        note_sequence_ch = token_sequence_to_note_sequence(content,NOTE_LENGTH_16TH_120BPM = (1/(tdelta)) * 60/120, BAR_LENGTH_120BPM = 4* 60 / 120)
        #note_seq.plot_sequence(note_sequence_ch,ax=ax)
        
        # Exemple d'utilisation
        marker_times = []
        for mark in range(end_bar-begin_bar+1):
            marker_times.append((mark+1) * 4 * 60 / 120)
        plot_sequence(note_sequence_ch, marker_times=marker_times)



        note_seq.play_sequence(note_sequence_ch) 
       
 
    else:
        print("No notes to display.")