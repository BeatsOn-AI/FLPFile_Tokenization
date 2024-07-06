# FLP Reader and Tokenizer

This repository contains a Python implementation for reading and tokenizing FL Studio project files (FLP). It provides functionality to convert FLP files into a structured composition format and offers tools to generate datasets from these compositions.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [FLP Handler](#flp-handler)
  - [FLP Dataset](#flp-dataset)
- [Examples](#examples)
- [Dependencies](#dependencies)

## Installation

To use this code, you need to install the required Python packages. You can do this by running:

```bash
pip install tqdm pyflp note-seq
```

## Usage

### FLP Handler

The `FLP_handler` class is designed to read and tokenize a single FLP file.

#### Initialization

```python
from FLP import FLP_handler
handler = FLP_handler(flp_file, time_delta)
```
#### Plot and Play a Handler
```python
handler.plotandplay(begin_bar, end_bar, nth) # Plots and plays the note sequence.
```

- `flp_file`: Path to the FLP file.
- `time_delta`: number of divisions of a quarter note.

#### Methods

```python
# Not Important
handler.list_patterns() # Lists the patterns and associated information in the FLP file.
handler.list_notes(track_info) # Lists the notes in the track information.
handler.pick_random_instrument() # Picks a random instrument ID.
handler.to_composition(track_final) # Converts track information to a structured composition format.
handler.is_empty(track, begin_bar, end_bar) # Checks if a track is empty between specified bars.
handler.to_note_sequence(begin_bar, end_bar, nth) # Converts a composition to a NoteSequence.
handler.get_composition() # Returns the composition.
handler.get_notes() # Returns the notes.
handler.get_project() # Returns the FLP project.
handler.get_track_info() # Returns the track information.
handler.to_textual(composition, begin_bar, end_bar) # Converts a composition to a textual format.
# Important
handler.plotandplay(begin_bar, end_bar, nth) # Plots and plays the note sequence.
handler.get_textual(begin_bar, end_bar) # Returns the textual format of the composition.
```

### FLP Dataset

The `FLP_Dataset` class is designed to handle multiple FLP files and generate datasets from them.

#### Initialization

```python
from FLP import FLP_Dataset
dataset = FLP_Dataset()
```

#### Methods

```python
dataset.parse_flp_files(folder) # Parses FLP files in the specified folder.
dataset.generate_dataset(folder, nb_files=10, time_delta=4, bar_size=8, nb_chunks=1, chunk_offset=2, complete=True) 
# Generates a dataset from FLP files.
# folder: Folder containing the FLP files.
# nb_files: Number of files to process.
# time_delta: Time delta parameter.
# bar_size: Size of each bar.
# nb_chunks: Number of chunks to generate.
# chunk_offset: Offset between chunks.
# complete: Whether to include only complete sequences.

dataset.__getitem__(index) # Gets the item at the specified index.
dataset.__len__() # Returns the length of the dataset.
```

## Examples

Here are some examples of how to use the \`FLP_handler\` and \`FLP_Dataset\` classes:

### Example 1: Handling a Single FLP File

```python
flp_file = 'path/to/your/flpfile.flp'
time_delta = 4

handler = FLP_handler(flp_file, time_delta)

if not handler.error:
    composition = handler.get_composition()
    textual_format, _, _ = handler.get_textual(1, 8)
    handler.plotandplay(1, 8)
else:
    print("Error reading the FLP file")
```

### Example 2: Generating a Dataset

```python
folder = 'path/to/your/flpfolder'
dataset = FLP_Dataset()
dataset, handlers, error_rate = dataset.generate_dataset(folder, nb_files=10, time_delta=4, bar_size=8, nb_chunks=2, chunk_offset=2, complete=True)

print(f"Generated {len(dataset)} sequences with an error rate of {error_rate}")
```

## Dependencies

- `tqdm`: For progress bars.
- `pyflp`: For parsing FLP files.
- `note_seq`: For note sequence visualization and playback.

Make sure to install these dependencies before running the code.

---

Feel free to explore the provided classes and methods to suit your needs for handling and tokenizing FLP files.