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

1. You'll be prompted to log in through Spotify

![Screen Shot 2021-12-10 at 12 44 25 AM](https://user-images.githubusercontent.com/52982928/145523417-1fd313e1-95c7-4565-859d-6eb464905b8b.png)
![Screen Shot 2021-12-10 at 12 44 46 AM](https://user-images.githubusercontent.com/52982928/145523452-0ff944c9-0b40-4f42-addc-a9b7a830f128.png)

2. Choose which feature you'd like to use

![Screen Shot 2021-12-10 at 12 48 56 AM](https://user-images.githubusercontent.com/52982928/145523854-57c0281f-1cc0-406d-91ad-7a9621f91b87.png)

4. View your most played tracks

![Screen Shot 2021-12-10 at 12 49 40 AM](https://user-images.githubusercontent.com/52982928/145523920-9006bcf2-f2c3-4162-9abe-e5798c2363c2.png)

5. View your most played artists

![Screen Shot 2021-12-10 at 12 50 24 AM](https://user-images.githubusercontent.com/52982928/145524004-b39d522b-ae46-4951-8d1f-8bb3bf38a335.png)

6. Get a custom playlist: choose the type of data your playlist is based on

![Screen Shot 2021-12-10 at 12 51 09 AM](https://user-images.githubusercontent.com/52982928/145524072-df3c0160-2bb0-4df5-8da6-ce458483927a.png)

7. Select the data that you'd like to base your playlist on, and name the playlist

![Screen Shot 2021-12-10 at 12 51 37 AM](https://user-images.githubusercontent.com/52982928/145524134-84e4b920-71e7-418e-a98b-b6e09211af04.png)
![Screen Shot 2021-12-10 at 12 52 48 AM](https://user-images.githubusercontent.com/52982928/145524272-33c64105-ace2-47eb-a5ed-b0793e597d1d.png)

8. View your playlist (also found in your Spotify library)

![Screen Shot 2021-12-10 at 12 53 58 AM](https://user-images.githubusercontent.com/52982928/145524394-b589949a-e9b2-4eff-96b3-3e52d483bab5.png)


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
