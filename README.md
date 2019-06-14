First, see "scoringAPI/scoring_engine/README.md".
It shows how engine works.



- POST Deploy testing

First, you should run server API and deploy API as follows.
	
	cd VoiceProcessor
	cd scoringAPI
	python3 server.py
	

Then, open Postman program and set options as follows:
	
	POST url:  localhost:5000/VoiceProcessor/word_scoring
	Params:    	voice: <audio-file>
				word: <word text>
				
	POST url:  localhost:5000/VoiceProcessor/sentence_scoring
	Params:    	voice: <audio-file>
				sentence: <sentence text>				
				