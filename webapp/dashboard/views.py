from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def index(request):
    
    default_part1 = open('./graphs/part1/part1_cat_count.html', 'r').read()
    default_part2 = open('./graphs/part2/part2_rand_for_featue_imp.html', 'r').read()
    default_part3 = open('./graphs/part3/part3_rf_hm.html', 'r').read()
    
    context = {'default_part1': default_part1, 'default_part2': default_part2, 'default_part3': default_part3}
    
    return render(request, 'dashboard_home.html', context)
    
def part1(request):
    user_select = request.GET.get('part1_dropdown')

    if int(user_select) == 1:
        graph = open('./graphs/part1/part1_cat_count.html', 'r').read()
    
    if int(user_select) == 2:
        graph = open('./graphs/part1/part1_like_vs_date.html', 'r').read()
        
    if int(user_select) == 3:
        graph = open('./graphs/part1/part1_dislike_vs_date.html', 'r').read()
        
    if int(user_select) == 4:
        graph = open('./graphs/part1/part1_views_vs_date.html', 'r').read()
    
    if int(user_select) == 5:
        graph = open('./graphs/part1/part1_avg_like.html', 'r').read()
        
    if int(user_select) == 6:
        graph = open('./graphs/part1/part1_avg_dislike.html', 'r').read()
        
    if int(user_select) == 7:
        graph = open('./graphs/part1/part1_avg_view.html', 'r').read()
        
    if int(user_select) == 8:
        graph = open('./graphs/part1/part1_dataset_used_bar.html', 'r').read()
        
    if int(user_select) == 9:
        graph = open('./graphs/part1/part1_dataset_used_pie.html', 'r').read()
        
    context = {'html_data': graph}
    
    return JsonResponse(context)

def part2(request):
    user_select = request.GET.get('part2_dropdown')

    if int(user_select) == 1:
        graph = open('./graphs/part2/part2_rand_for_featue_imp.html', 'r').read()
    
    if int(user_select) == 2:
        graph = open('./graphs/part2/part2_corr_mat.html', 'r').read()
        
    if int(user_select) == 3:
        graph = open('./graphs/part2/part2_pca.html', 'r').read()
        
    if int(user_select) == 4:
        graph = open('./graphs/part2/part2_dur_as_cat_with_target.html', 'r').read()
        
    if int(user_select) == 5:
        graph = open('./graphs/part2/part2_target_count.html', 'r').read()
    
    context = {'html_data': graph}
    
    return JsonResponse(context)

def part3(request):
    user_select = request.GET.get('part3_dropdown')

    if int(user_select) == 1:
        graph = open('./graphs/part3/part3_rf_hm.html', 'r').read()
    
    if int(user_select) == 2:
        graph = open('./graphs/part3/part3_model_compare.html', 'r').read()
        
    if int(user_select) == 3:
        graph = open('./graphs/part3/part3_sample_size_table.html', 'r').read()
        
    if int(user_select) == 4:
        graph = open('./graphs/part3/part3_sample_size_line.html', 'r').read()
    
    context = {'html_data': graph}
    
    return JsonResponse(context)