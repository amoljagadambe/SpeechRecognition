This software is a tool to recognize and evaluate phoneme of word.

The usage of this tool is as follows.

- Install dependency

First, you should install all dependencies using python.

Open terminal (or command prompt on Windows) and input following commands.

    sudo apt-get install swig libpulse-dev libasound2-dev
    sudo pip3 install pocketsphinx    
    sudo pip3 install -r requirement.txt
    
   
- Usage

After installing of dependency library, you can use it using arguments like below.


    python3 syllableScoring.py --dir <data_folder>
    
	Before it, you should put sample files under <data_folder> and file names should same as word text.
	
	File names:
		# filename:  <speaker>-<word>-<revision>
	for example,  shan-america-01.wav
	
	The result will be saved in 'test_scoring.csv' file.


- Word alignment and scoring

    python3 word_alignment.py --dir <data_folder>

    Here, if there is a word which is not in the dictionary, following message will be printed in terminal.
    
        There were words not found in the dictionary. Would you like to abort to fix them? (Y/N)
        
    Then, you can continue with inputting "N" or "n".
    
    This result will be saved in 'word_alignment.csv' file.
    
    
**************************************************
1) Phoneme scoring system
2) Syllable extraction with timestamp in audio file of a word
3) Scoring by syllable unit
4) Word alignment in audio of one sentence
