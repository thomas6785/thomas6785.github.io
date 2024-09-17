import pickle
from os import listdir
from operator import itemgetter
from datetime import datetime

class Post():
    def __init__(self, title, body, ):
        self.title = title
        self.body = body
        self.created_date = datetime.now()

def load():
    # Get a list of available pickles
    files = listdir("pickled_post_files")
    
    # Extract their timestamp
    timestamped_files = [ (filename,datetime.strptime(files[0],"posts_backup_%Y-%m-%d_%H-%M-%S.pkl")) for filename in files ]

    # Identify the most up-to-date
    most_recent_file = sorted(timestamped_files,key=itemgetter(0))[-1][0]
    
    # Read in the file's data
    with open("pickled_post_files/"+most_recent_file,mode="rb") as file:
        posts = pickle.loads(file.read())
    
    print("Got posts from "+most_recent_file)
    return posts

def save(filename=""):
    global posts

    if not(filename):
        filename = datetime.now().strftime("posts_backup_%Y-%m-%d_%H-%M-%S.pkl")
    
    with open("pickled_post_files/"+filename,mode="wb") as file:
        file.write(pickle.dumps(posts))

if __name__=='__main__':
    print()
    posts = load()