from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import pickle
import requests
import json
# Create your views here.
loaded_model = pickle.load(open("account/model.sav","rb"))
default_pfp = "https://instagram.fmlg9-1.fna.fbcdn.net/v/t51.2885-19/464760996_1254146839119862_3605321457742435801_n.png?stp=dst-jpg_e0_s150x150_tt6&cb=8577c754-c2464923&_nc_ht=instagram.fmlg9-1.fna.fbcdn.net&_nc_cat=1&_nc_oc=Q6cZ2QFED5l6eawI3561OmgS-R0FfqjZ4Auw_PhJycqZXYq6QFFT2EYkf1Kb6zbXvaBIhsE&_nc_ohc=IffVxQ5s3Q0Q7kNvwFPssZC&_nc_gid=WeyAeCgfSvlhIF2ptiYl-Q&edm=ALlQn9MBAAAA&ccb=7-5&ig_cache_key=YW5vbnltb3VzX3Byb2ZpbGVfcGlj.3-ccb7-5-cb8577c754-c2464923&oh=00_AfG3W10SFKKz9Z7EKZ0pybubglnP-rbBSj_YhbP7x4uWKA&oe=6812ACA8&_nc_sid=e7f676"



def index(request):
    return render(request,"account/index.html")

def valid_link(link):
    pass

def num_to_char(string):
    if len(string)==0:
        return 0
    count=0
    for c in string:
        if c >= '0' and c<='9':
            count += 1
    return count/len(string)

def tokens(string: str):
    x = string.split(", _.")
    return len(x)

def get_details(username):
    """Details are:
       has_pfp
       ratio of num of numerical chars to length in username
       full name in word tokens
       ratio of num of numerical chars to length in full name
       is username == fullname
       bio length in characters
       has external_url ?
       private ?
       no. of posts
       no. of followers

    """
    header = {"User-Agent": "Instagram 219.0.0.12.117 Android"}
    response = requests.get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}", headers=header)
    js = json.loads(response.content)
    js = js["data"]["user"]
    full_name = js["full_name"]
    bio = js["biography"]
    pfp_url = js["profile_pic_url"]
    external_urls = js["bio_links"]
    is_private = js["is_private"]
    followers = js["edge_followed_by"]["count"]
    following = js["edge_follow"]["count"]
    posts = js["edge_owner_to_timeline_media"]["count"]
    features = [None]*11
    features[0] = (pfp_url != default_pfp)
    features[1] = num_to_char(username)
    features[2] = tokens(full_name)
    features[3] = num_to_char(full_name)
    features[4] = str(username).lower == str(full_name).lower
    features[5] = len(bio)
    features[6] = len(external_urls) > 0
    features[7] = is_private
    features[8] = posts
    features[9] = followers
    features[10] = following
    return features
    

def check(request):
    #link = request.GET['url']
    username = request.GET['username']
    features = get_details(username)
    result = loaded_model.predict([features])
    return render(request, "account/results.html", {
        "features": features,
        "result": result[0]
    })
    