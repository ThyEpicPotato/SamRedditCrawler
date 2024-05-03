import praw
import json
import time
from praw.exceptions import PRAWException, APIException
from prawcore.exceptions import ResponseException

# Helper Variables
postCount = 0
postLimit = 5000

# Reddit developer account: 
ID          = "dhEQFnUAHSZc4kXHZN-AJw"
SECRET      = "ouK2JNVZnBMlUkMOY0RyFwFcCTBB9g"
AGENT       = "cs172"

# Json setup:
items = []
fields = ('permalink', 'id', 'title', 'url','selftext','score', 'upvote_ratio', 'created_utc', 'num_comments')
#           link                      image  text-body  upvotes                  time created
# import requests
# from bs4 import BeautifulSoup
# seed = "https://en.wikipedia.org/wiki/Randomness"

# page = requests.get(seed)
# soup = BeautifulSoup(page.content, "html.parser")

# for link in soup.find_all('a'):
#     # do whatever with links here
#     print("hi")


# Reddit read only mode
reddit = praw.Reddit(
    client_id=ID,
    client_secret=SECRET,
    user_agent=AGENT
)

for post in reddit.subreddit("Cooking").new(limit=postLimit):
    # grab dictionary with attributes of object using vars()
    while True:
        try:
            # Rate limiting
            time.sleep(0.5)
            postCount += 1
            
            to_dict = vars(post)
            print(f"Parsing: ({post.title})[{postCount}:{postLimit}]")
        
            # grab specific attributes specified in fields, written above, for current post
            sub_dict = {field:to_dict[field] for field in fields}
        
            # grab all comments for the current post
            comments = []
            post.comments.replace_more(limit=None)
            # Helper counter for comments
            commentCount = 0
            print("Downloading Comments . . . ")
            for comment in post.comments.list():
                comments.append(comment.body)
                commentCount += 1
            print(commentCount)
            sub_dict['comments'] = comments
        
            # Create a new container that just has the field we want
            items.append(sub_dict)
            
            if postCount >= postLimit:
                raise StopIteration
    
            break
            
        except ResponseException as e:
            if e.response.status_code == 429:
                # Handle rate limiting
                print("Rate limited. Retrying after 5 seconds...")
                time.sleep(5)
            else:
                # Handle other HTTP errors
                print(f"HTTP Error: {e}")
                break
                
        except (PRAWException, APIException) as e:
            # Handle other PRAW exceptions
            print(f"Exception: {e}")
            break

# for item in items:
#     print(item)
# Dump into json format and write to crawl.json
json_str = json.dumps(items)
with open('Cooking.json', 'w') as f:
    json.dump(items, f)
