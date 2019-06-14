hotelwiki-observer
-------

Customer Behavioural Prediction Application

Install
-------
## clone the repository
    git clone https://github.com/amoljagadambe/SpeechRecognition.git
    cd SpeechRecognition
    # checkout the correct version
    git tag  # shows the tagged versions
    git checkout latest-tag-found-above
    
Create a virtualenv in the flask-application directory and activate it::

    python -m venv venv
    venv\Scripts\activate.bat
    
Install Dependencies in Virtual Environment::

    pip install swig libpulse-dev libasound2-dev
    pip install -r requirements.txt
    pip install pocketsphinx 
    
 RUN
 ---
 
 On Virtual Environment::
    
    set FLASK_APP=run.py
    flask run
    
Open http://127.0.0.1:5000 in a browser.