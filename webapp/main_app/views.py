from django.shortcuts import render
from django.http import JsonResponse
from main_app import data_generator
from main_app import prediction_helper
from main_app import database_helper

# Create your views here.

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
MODEL_PATH = './models/rfclf.joblib.pkl'


def index(request):
    return render(request, 'main_app_homepage.html')

def standups(request):
    return render(request, 'standups.html')

def process_url(request):

    if request.method == 'POST':
        video_id = request.POST.get('youtube_submit_input')

        if 'youtube.com' in video_id:
            video_id = video_id.split('watch?v=')[-1]

        # Helps to get only the video ID characters
        video_id = video_id[:11]

        # we will want to save user input irrespective of whether 24 hours has passed
        # this might be a good metric to understand the popularity of a video in youtube.

        database_helper.save_user_input(video_id) # save user input to UserInput table
        
        request.session['video_id'] = video_id
        
        if not database_helper.check_if_24_hours_passed(video_id):
            json_data = database_helper.get_old_records(video_id)
            json_data['status'] =  2
            
            return JsonResponse(json_data)
            
        else:
            url = data_generator.check_link(video_id, USER_AGENT)

            if url == 'Video not found':
                json_data = {'status': 3}
            
            else:
                json_data = data_generator.get_video_meta(url)
                json_data['status'] = 1

                meta_df, comments_df = data_generator.create_dataframe_for_prediction(json_data)
                final_df, json_data = prediction_helper.create_final_dataframe(json_data, comments_df, meta_df)

                prediction = prediction_helper.make_pred(final_df, MODEL_PATH)[0]

                if prediction == -1:
                    json_data['prediction'] = 'negative'
                elif prediction == 0:
                    json_data['prediction'] = 'neutral'
                else:
                    json_data['prediction'] = 'positive'
                    
                database_helper.save_video_meta(json_data) # save meta data to VideoMeta table
                database_helper.save_video_comments(video_id, json_data['comments']) # save comments to Comments table

        return JsonResponse(json_data)

def user_select_positive(request):
    if request.method=='GET':
        video_id = request.session['video_id']
        
        database_helper.save_user_select_positive(video_id, 'positive') # save positive user selection to table

        return JsonResponse({'status': 'user select saved successfully'})

def user_select_negative(request):
    if request.method=='GET':
        video_id = request.session['video_id']
        
        database_helper.save_user_select_positive(video_id, 'positive') # save negative user selection to table

        return JsonResponse({'status': 'user select saved successfully'})
