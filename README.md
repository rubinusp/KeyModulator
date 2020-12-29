# Key Modulator: A Music Tool
Key Modulator is a tool for shifting the key of a song to another. Currently it supports command-line methods.

* It only supports WAV files currently

### Demo
Original song: https://www.youtube.com/watch?v=ZOHsd6Zk7DM&ab_channel=TimelessMusic

Modulated song (+4): https://soundcloud.com/gordon-poon-488991482/lydia_modulated/s-mMRC2RMO9yV

## Purpose
Singers often find it difficult to learn new songs with high pitches. Before they can master the pitches, it is best to 
lower the key of songs so that the singers may focus on other aspects of the songs first. The tool is designed to help 
faciliate the key modulation process with great efficiency.

## Installation
1) Clone this repository via `git clone`
2) Navigate the terminal to the working directory of the repository
3) Install the module dependency using pip

```
pip install matplotlib numpy scipy
```

3) Check that the program can be run by typing:

```
python KeyModulator.py --help
``` 
    
   This should display an usage statement of the program
    
* Use `pip3` and `python3` instead for python version 3.0 or above
    
## Usage

```
python KeyModulator.py [option] <inputfile> <outputfile> <shift>
```

* **Inputfile**: it specifies the path to the song for modulation
* **Outputfile**: it specifies the path for the modulated song
* **Shift**: it is an integer which indicates the number of semitones to be shifted
    * It is best to shift within [-7, 7] to retain relative quality
    * Example: -2 indicates the key will be decreased by 2 semitones. If the song is in A major, it will be shifted to G 
    major
    
## How It Works
1. The program reads the audio into a `numpy` array and extract the song properties such as `sample_rate`, `n_channels`, 
    etc.
2. It creates frames of the audio samples with certain overlapping
3. It applies the Hanning window to the frames to minimize frame discontinuity
4. It synthesizes the frames into a new audio, with each frame overlapping more/less (i.e. decreasing/increasing the hop
    size of the frames). This will shorten/lengthen the new song
5. It resamples the new song using the original sampling rate by linear interpolation. This will change the duration of 
    the new song back to the same duration of the original but result different frequencies from the original. Different
    frequencies are therefore perceived as different keys.
    
* FFT is never performed during the algorithm. This will largely increase the efficiency. 
    
## Future Works
* Use FFT method as an optional method
* Support more audio formats
* Support GUI tools
  
