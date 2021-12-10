# **SpotiBuddy**

SpotiBuddy is a website used to track your listening on Spotify. It allows you to view your most played tracks and artists over the last six months, month, or of all time. 
Spotify's famous 'Wrapped' feature only releases at the end of the year to show your listening, but SpotiBuddy can be accessed at any time. The web application also has a recommendation feature.
The site designs a new, personalized playlist that is based on the user's most streamed artists, tracks, and genres.

### **Technologies Used:**
- Python (Flask, sqlalchemy, spotipy)
- HTML (Jinja2)
- CSS
- Spotify API

### **Walkthrough**

### **Usage**
1. Ensure you have Python, Flask, and spotipy installed
```
$ pip install python
$ pip install flask
$ pip install spotipy
```
1. Clone the repository locally
```
$ git clone https://github.com/Visheshss/SpotiBuddy.git
```
2. Navigate to SpotiBuddy
```
$ cd SpotiBuddy
```
3. Set FLASK_APP and the database URL
```
$ export FLASK_APP=application.py
```
4. Run the application
```
$ flask run
```
