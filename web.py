from flask import Flask, render_template, request, jsonify
import sqlite3
import json
from flask import g
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import concurrent.futures

app = Flask(__name__)

#Get API key
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

MOVIE_API_KEY = '5583ad55567467b684e3964398e11314'
MOVIE_API_ENDPOINT = 'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

token = get_token()

def get_auth_header(token):
    return{"Authorization": "Brearer " + token}

def search_songs_by_genres(client_id, client_secret, genres):
    if not genres:
        return []


    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


   
    songs = []
    for genre in genres:
        recommendations = sp.recommendations(seed_genres=[genre], limit=10)


    for track in recommendations['tracks']:
            song_info = {
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
            }
            songs.append(song_info)
    return songs



#临时
with open("data.json","r") as json_file:
    all_recommendations = json.load(json_file)


# Save all recommendations to a single JSON file
#with open('all_recommendations.json', 'w') as rec_file:
#    json.dump(all_recommendations, rec_file)

DATABASE = 'user_data.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def save_user_input(mbti_type):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO user_data (mbti_type) VALUES (?)', (mbti_type,))
    db.commit()

def get_user_input():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT mbti_type FROM user_data')
    return [row[0] for row in cursor.fetchall()]

def get_recommendations(mbti_type):
    return all_recommendations[mbti_type]


#Web direction
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    mbti_type = request.form.get('mbti')

    if mbti_type not in all_recommendations:
        return render_template('error.html', error_message='Invalid MBTI type')
    
    save_user_input(mbti_type)
    recommendations = get_recommendations(mbti_type)
    return render_template('recommend.html', mbti_type=mbti_type, recommendations=recommendations)

overview_data = {
    'ISFJ': 'Quiet, serious, earn success by being thorough and dependable. Practical, matter-of-fact, realistic, and responsible. Decide logically what should be done and work toward it steadily, regardless of distractions. Take pleasure in making everything orderly and organized—their work, their home, their life. Value traditions and loyalty.',
    'INFJ': 'Seek meaning and connection in ideas, relationships, and material possessions. Want to understand what motivates people and are insightful about others. Conscientious and committed to their firm values. Develop a clear vision about how best to serve the common good. Organized and decisive in implementing their vision.',
    'INTJ': 'Have original minds and great drive for implementing their ideas and achieving their goals. Quickly see patterns in external events and develop long-range explanatory perspectives. When committed, organize a job and carry it through. Skeptical and independent, have high standards of competence and performance—for themselves and others.',
    'ISTP': 'Tolerant and flexible, quiet observers until a problem appears, then act quickly to find workable solutions. Analyze what makes things work and readily get through large amounts of data to isolate the core of practical problems. Interested in cause and effect, organize facts using logical principles, value efficiency.',
    'ISFP': 'Quiet, friendly, sensitive, and kind. Enjoy the present moment, what Is going on around them. Like to have their own space and to work within their own time frame. Loyal and committed to their values and to people who are important to them. Dislike disagreements and conflicts; do not force their opinions or values on others.',
    'INFP': 'Idealistic, loyal to their values and to people who are important to them. Want to live a life that is congruent with their values. Curious, quick to see possibilities, can be catalysts for implementing ideas. Seek to understand people and to help them fulfill their potential. Adaptable, flexible, and accepting unless a value is threatened.',
    'INTP': 'Seek to develop logical explanations for everything that interests them. Theoretical and abstract, interested more in ideas than in social interaction. Quiet, contained, flexible, and adaptable. Have unusual ability to focus in depth to solve problems in their area of interest. Skeptical, sometimes critical, always analytical.',
    'ESTP': 'Flexible and tolerant, take a pragmatic approach focused on immediate results. Bored by theories and conceptual explanations; want to act energetically to solve the problem. Focus on the here and now, spontaneous, enjoy each moment they can be active with others. Enjoy material comforts and style. Learn best through doing.',
    'ESFP': 'Outgoing, friendly, and accepting. Exuberant lovers of life, people, and material comforts. Enjoy working with others to make things happen. Bring common sense and a realistic approach to their work and make work fun. Flexible and spontaneous, adapt readily to new people and environments. Learn best by trying a new skill with other people.',
    'ENFP': 'Warmly enthusiastic and imaginative. See life as full of possibilities. Make connections between events and information very quickly, and confidently proceed based on the patterns they see. Want a lot of affirmation from others, and readily give appreciation and support. Spontaneous and flexible, often rely on their ability to improvise and their verbal fluency.',
    'ENTP': 'Quick, ingenious, stimulating, alert, and outspoken. Resourceful in solving new and challenging problems. Adept at generating conceptual possibilities and then analyzing them strategically. Good at reading other people. Bored by routine, will seldom do the same thing the same way, apt to turn to one new interest after another.',
    'ESTJ': 'Practical, realistic, matter-of-fact. Decisive, quickly move to implement decisions. Organize projects and people to get things done, focus on getting results in the most efficient way possible. Take care of routine details. Have a clear set of logical standards, systematically follow them and want others to also. Forceful in implementing their plans.',
    'ESFJ': 'Warmhearted, conscientious, and cooperative. Want harmony in their environment, work with determination to establish it. Like to work with others to complete tasks accurately and on time. Loyal, follow through even in small matters. Notice what others need in their day-to-day lives and try to provide it. Want to be appreciated for who they are and for what they contribute.',
    'ENFJ': 'Warm, empathetic, responsive, and responsible. Highly attuned to the emotions, needs, and motivations of others. Find potential in everyone, want to help others fulfill their potential. May act as catalysts for individual and group growth. Loyal, responsive to praise and criticism. Sociable, facilitate others in a group, and provide inspiring leadership.',
    'ENTJ': 'Frank, decisive, assume leadership readily. Quickly see illogical and inefficient procedures and policies, develop and implement comprehensive systems to solve organizational problems. Enjoy long-term planning and goal setting. Usually well informed, well read, enjoy expanding their knowledge and passing it on to others. Forceful in presenting their ideas.'
    # Add other MBTI types as needed
}

@app.route('/overview')
def overview():
    mbti_type = request.args.get('mbti')

    text_content = overview_data.get(mbti_type, f"No content available for MBTI type: {mbti_type}")
    return render_template('overview.html', mbti_type=mbti_type, text_content=text_content)

@app.route('/movies')
def movies():
    mbti_type = request.args.get('mbti')

    if mbti_type is not None and mbti_type in all_recommendations:
        recommended_movies = all_recommendations[mbti_type].get('movies', [])
    else:
        # Handle the case where 'mbti_type' is None or not present in the dataset
        recommended_movies = []

    return render_template('movies.html', mbti_type=mbti_type, movierecommended_movies_data=recommended_movies)

@app.route('/music')
def music():
    mbti_type = request.args.get('mbti')

    if mbti_type is not None and mbti_type in all_recommendations:
        recommended_songs = all_recommendations[mbti_type].get('songs', [])
    else:
        # Handle the case where 'mbti_type' is None or not present in the dataset
        recommended_songs = []

    return render_template('music.html', mbti_type=mbti_type, recommended_songs=recommended_songs)

@app.context_processor
def inject_previous_user_inputs():
    return dict(previous_user_inputs=get_user_input())

if __name__ == '__main__':
    app.run(debug=True)

