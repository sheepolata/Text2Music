dict_notes2freqs = {
    # "C3" : 130.81,
    # "D3" : 146.83,
    # "E3" : 164.81,
    # "F3" : 174.61,
    # "G3" : 196.00,
    # "A3" : 220.00,
    # "B3" : 246.94

	# "C4" : 261.63,
	# "D4" : 293.66,
	# "E4" : 329.63,
	# "F4" : 349.23,
	# "G4" : 392.00,
	# "A4" : 440.00,
	# "B4" : 493.88

    "C5" : 523.25,
    "D5" : 587.33,
    "E5" : 659.25,
    "F5" : 698.46,
    "G5" : 783.99,
    "A5" : 880.00,
    "B5" : 987.77

}

dict_freqs2notes = {}

for k in dict_notes2freqs.keys():
    dict_freqs2notes[dict_notes2freqs[k]] = k

list_note2freqs = list(dict_freqs2notes.keys())