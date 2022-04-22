from main_app.models import *
from datetime import datetime


def check_if_24_hours_passed(video_id):
    """
    This function will check if the specified video_id exists in the VideoMeta table.

    If the data exists, this function will also check for the last time the data was updated 
    (check the updated_at column). If the updated date is less than 24 hours, the function will 
    return False else it will return True

    Args:
        video_id (str): Youtube video ID

    Returns:
        bool: True if 24 hours have passed since lass update
    """

    if VideoMeta.objects.filter(youtube_video_id=video_id).exists():
        record = VideoMeta.objects.get(youtube_video_id=video_id)
        updated_at = record.list_data()[-1]
        tz_info = updated_at.tzinfo
        current_time = datetime.now(tz_info)
        difference = current_time - updated_at

        if difference.days == 0:
            return False  # this is returning False because 24 hours have not yet passed since the last update

        return True

    else:
        # the required record does not exist in the table
        return True

def save_user_input(video_id):
    """
    This function will save the user input to the UserInput table

    Here user input refers to the video_id or the youtube url that the user searches for 
    in the webapp

    Args:
        video_id (str): youtube video ID

    Returns:
        str: success message
    """
    new_user_input = UserInput(youtube_video_id=video_id)
    new_user_input.save()

    return "User input saved to UserInput table"

def save_video_meta(json_data):
    """
    Function to save meta_record.list_data() data of a specified vieo to the VideoMeta table 

    Args:
        json_data (dict):   all the meta_record.list_data() information retrieved for a video. To know more 
                            about the kind of information that is extracted or how theyh are extracted
                            look at main_app.prediction_helper

    Returns:
        str: success message
    """
    new_record = VideoMeta(
        youtube_video_id=json_data['video_id'],
        title=json_data['title'],
        desc=json_data['description'],
        tags="|".join(json_data['tags']),
        duration=json_data['duration'],
        age_limit=json_data['age_limit'],
        view_count=json_data['views'],
        like_count=json_data['likes'],
        view_like_ratio_smoothed=json_data['view_like_ratio_smoothed'],
        is_comments_enabled=json_data['is_comments_enabled'],
        is_live_content=json_data['is_live_content'],
        cat_codes=json_data['category'],
        desc_neu=json_data['desc_neu'],
        desc_neg=json_data['desc_neg'],
        desc_pos=json_data['desc_pos'],
        desc_compound=json_data['desc_compound'],
        comments_neu=json_data['comment_neu'],
        comments_neg=json_data['comment_neg'],
        comments_pos=json_data['comment_pos'],
        comments_compound=json_data['comment_compound'],
        votes=json_data['votes'],
        no_comments_binary=json_data['no_comment_binary'],
        model_prediction=json_data['prediction'],
        comment_count = json_data['comments_count'],
        date_published = json_data['date_published'],
        channel_name = json_data['channel']['name'],
        channel_id = json_data['channel']['channel_id']
    )

    new_record.save()

    return "Meta data of video save to VideoMeta table"

def save_video_comments(video_id, comments_data):
    """
    Function to save the comments extracted for a video.

    Args:
        video_id (str): Youtube video ID
        comments_data (list | str): If comments exist then comments_data will be a list of dicts. 
                                    Else it will be 'none'

    Returns:
        str: success message
    """
    
    if comments_data != 'none':
        if Comments.objects.filter(youtube_video_id=video_id).exists():
            print('comments already exist')
            print('deleting the existing comments')
            Comments.objects.filter(youtube_video_id=video_id).delete()

        for comment in comments_data:
            new_comments_record = Comments(
                youtube_video_id=comment['video_id'],
                cid=comment['cid'],
                text=comment['text'],
                time=comment['time'],
                author=comment['author'],
                channel=comment['channel'],
                votes=comment['votes'],
                heart=comment['heart']
            )

            new_comments_record.save()

    return "All comments have been saved to the Comments table"

def save_user_select_positive(video_id, sentiment):
    """
    Function to save user selection to the UserTargetSelect table

    Here user selection refers to the correct prediction according to the user. 
    This data can later be used to train the model again to increase accuracy

    Args:
        video_id (str): Youtube video ID
        sentiment (str): User selection: Positive or Negative

    Returns:
        str: success message
    """
    new_user_target = UserTargetSelect(
        youtube_video_id=video_id,
        user_prediction=sentiment
    )

    new_user_target.save()

    return f"User selection {sentiment} saved"

def get_old_records(video_id):

    meta_queryset = VideoMeta.objects.filter(youtube_video_id=video_id)
    comments_queryset = Comments.objects.filter(youtube_video_id=video_id)

    json_data = {}
    json_data['channel'] = {}

    for meta_record in meta_queryset:
        print(meta_record.list_data())
        json_data['title'] = meta_record.list_data()[1]
        json_data['description'] = meta_record.list_data()[2]
        json_data['tags'] = meta_record.list_data()[3].split('|')
        json_data['duration'] = meta_record.list_data()[4]
        json_data['age_limit'] = meta_record.list_data()[5]
        json_data['views'] = meta_record.list_data()[6]
        json_data['likes'] = meta_record.list_data()[7]
        json_data['view_like_ratio_smoothed'] = meta_record.list_data()[8]
        json_data['is_comments_enabled'] = meta_record.list_data()[9]
        json_data['is_live_content'] = meta_record.list_data()[10]
        json_data['category'] = meta_record.list_data()[11]
        json_data['desc_neu'] = meta_record.list_data()[12]
        json_data['desc_neg'] = meta_record.list_data()[13]
        json_data['desc_pos'] = meta_record.list_data()[14]
        json_data['desc_compound'] = meta_record.list_data()[15]
        json_data['comment_neg'] = meta_record.list_data()[16]
        json_data['comment_neu'] = meta_record.list_data()[17]
        json_data['comment_pos'] = meta_record.list_data()[18]
        json_data['comment_compound'] = meta_record.list_data()[19]
        json_data['votes'] = meta_record.list_data()[20]
        json_data['no_comment_binary'] = meta_record.list_data()[21]
        json_data['prediction'] = meta_record.list_data()[22]
        json_data['comments_count'] = meta_record.list_data()[23]
        json_data['date_published'] = meta_record.list_data()[24]
        json_data['channel']['name'] = meta_record.list_data()[25]
        json_data['channel']['channel_id'] = meta_record.list_data()[26]

    comments_list = []
    for comment_record in comments_queryset:
        comments_dict = {}
        comments_dict['cid'] = comment_record.list_data()[1]
        comments_dict['text'] = comment_record.list_data()[2]
        comments_dict['time'] = comment_record.list_data()[3]
        comments_dict['author'] = comment_record.list_data()[4]
        comments_dict['channel'] = comment_record.list_data()[5]
        comments_dict['votes'] = comment_record.list_data()[6]
        comments_dict['heart'] = comment_record.list_data()[7]
        comments_dict['video_id'] = comment_record.list_data()[0]
            
        comments_list.append(comments_dict)

    json_data['comments'] = comments_list
    json_data['embed_url'] = f"https://www.youtube.com/embed/{video_id}"
    json_data['channel']['url'] = f"https://www.youtube.com/channel/{json_data['channel']['channel_id']}"

    return json_data