import requests
import os
import pandas as pd
import googleapiclient.discovery
from main_app.comments_download import get_comments

def check_link(video_id, user_agent):
    """
    This function will validate the video ID provided by the user.
    If the video ID is wrong or for some reason the video is no longer available in youtube,
    the function will return a string "video not found". Else the html data will be returned.

    Args:
        video_id (str): Unique ID for a video in youtube.
        user_agent (str): characteristic string for networks to identify the request.

    Returns:
        str: The html data or the error message
    """

    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    session = requests.Session()
    session.headers['User-Agent'] = user_agent

    try:
        response = session.get(youtube_url)
        print('video received')
    except:
        return 'Video not found'

    if 'uxe=' in response.request.url:
        session.cookies.set('CONSENT', 'YES+cb', domain='.youtube.com')
        response = session.get(youtube_url)

    html = response.text

    error_pattern = '"playabilityStatus":{"status":"ERROR","reason":"Video unavailable"'

    if error_pattern in html:
        return 'Video not found'

    return youtube_url

def create_api_session():
    """
    This function starts a youtube API session. 
    The function expects the youtube API keys to be stored as environment variables.

    Returns:
        _type_: The youtube API session
    """
    DEVELOPER_KEY = os.environ['YOUTUBE_API_KEY2']
    api_service_name = "youtube"
    api_version = "v3"

    return googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

def clean_duration(text):
    """
    This function will convert the duration attribute obtained from the youtube API
    and convert them into minutes. The duration should be of the format `PT...`

    The duration may be Days, hours, minutes or seconds long

    Args:
        text (str): The duration of a video obtained using the youtube API

    Returns:
        float: the duration converted to minutes
    """
    days_to_minutes = 0
    hours_to_minutes = 0
    minutes = 0
    seconds_to_minutes = 0

    text = text.replace('PT', '')

    for i in ['D', 'H', 'M', 'S']:
        text = text.replace(i, ':')

    lst = text.split(':')
    lst = [int(x) for x in lst if x]

    if len(lst) == 4:
        days_to_minutes = lst[0] * 24 * 60
        hours_to_minutes = lst[1] * 60
        minutes = lst[2]
        seconds_to_minutes = lst[3] / 60

    if len(lst) == 3:
        hours_to_minutes = lst[0] * 60
        minutes = lst[1]
        seconds_to_minutes = lst[2] / 60

    if len(lst) == 2:
        minutes = lst[0]
        seconds_to_minutes = lst[1] / 60

    else:
        seconds_to_minutes = lst[0] / 60

    return days_to_minutes + hours_to_minutes + minutes + seconds_to_minutes

def get_video_meta(url):
    """
    This function gets additional information on a given video. 
    This function will call the `get_meta_with_soup` function and also use the 
    youtube API to get all the required information.

    Args:
        url (str): the youtube url to be parsed

    Returns:
        dict: All the meta information on the video collected.
    """

    result = {}

    youtube = create_api_session()

    youtube_video_id = url.split('v=')[-1]  # video id

    youtube_video_api_response = youtube.videos().list(
        part="statistics,contentDetails,snippet,status,id",
        id=youtube_video_id
    ).execute()

    result["title"] = youtube_video_api_response['items'][0]['snippet'].get('title')
    result["views"] = int(youtube_video_api_response['items'][0]['statistics'].get('viewCount', 0))
    
    pub_date = "".join(" ".join(youtube_video_api_response['items'][0]['snippet'].get('publishedAt').split('T')).split("Z"))
    result["date_published"] = pub_date
    
    all_tags = youtube_video_api_response['items'][0]['snippet'].get('tags')
    if all_tags:
        result["tags"] = youtube_video_api_response['items'][0]['snippet'].get('tags')
    else:
        result["tags"] = []
        
    result["likes"] = int(youtube_video_api_response['items'][0]['statistics'].get('likeCount', 0))

    channel_name = youtube_video_api_response['items'][0]['snippet'].get('channelTitle')
    channel_id = youtube_video_api_response['items'][0]['snippet'].get('channelId')
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    channel_subscribers = None

    result['channel'] = {'name': channel_name, 'channel_id': channel_id, 'url': channel_url, 'subscribers': channel_subscribers}

    if 'commentCount' in youtube_video_api_response['items'][0]['statistics'].keys():
        result['comments_count'] = youtube_video_api_response['items'][0]['statistics']['commentCount']
        result['is_comments_enabled'] = True

    else:
        result['comments_count'] = None
        result['is_comments_enabled'] = False

    result['video_id'] = youtube_video_id

    result["description"] = youtube_video_api_response['items'][0]['snippet'].get('description')

    is_live = youtube_video_api_response['items'][0]['snippet'].get('liveBroadcastContent')
    if is_live == 'none':
        result["is_live_content"] = 0
    else:
        result["is_live_content"] = 1

    # this category will only return category ID
    result['category'] = int(youtube_video_api_response['items'][0]['snippet'].get('categoryId'))

    result['embed_url'] = f"https://www.youtube.com/embed/{youtube_video_id}"

    if 'contentRating' in youtube_video_api_response['items'][0]['snippet'].keys():
        result['age_limit'] = 18
    else:
        result['age_limit'] = 0

    # get and clean duration
    duration_in_string = youtube_video_api_response['items'][0]['contentDetails'].get('duration').split('PT')[-1]
    result['duration_string'] = duration_in_string
    result['duration'] = clean_duration(duration_in_string)

    extracted_comments = get_comments(youtube_video_id, sort_by=0)
    if extracted_comments:
        result['comments'] = extracted_comments
    else:
        result['comments'] = 'none'

    return result

def create_dataframe_for_prediction(meta_data):

    if meta_data['comments'] != 'none':
        comments_df = pd.DataFrame(meta_data['comments'])
    else:
        comments_df = None

    new_dict = {}
    new_dict['id'] = meta_data['video_id']
    new_dict['desc_text'] = meta_data['description']
    new_dict['view_count'] = meta_data["views"]
    new_dict['like_count'] = meta_data["likes"]
    new_dict['age_limit'] = meta_data['age_limit']
    new_dict['duration'] = meta_data['duration']
    new_dict['is_comments_enabled'] = meta_data['is_comments_enabled']
    new_dict['is_live_content'] = meta_data['is_live_content']
    new_dict['cat_codes'] = meta_data['category']
    new_dict['NoCommentsBinary'] = 0

    if meta_data['comments'] == 'none':
        new_dict['NoCommentsBinary'] = 1

    meta_df = pd.DataFrame(new_dict, index=[0])

    return meta_df, comments_df