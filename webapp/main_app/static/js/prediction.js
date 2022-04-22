function youtube_link_form_submit(event) {
    event.preventDefault();
    var data = new FormData($('#youtube_link_form').get(0));

    $.ajax({
        url: $(this).attr('action'),
        type: $(this).attr('method'),
        data: data,
        cache: false,
        processData: false,
        contentType: false,

        beforeSend: function () {
            $('.loading_gif_container').css('display', 'block');
            $(".video_deets").load(" .video_deets");
        },

        complete: function () {
            $('.loading_gif_container').css('display', 'none');
        },

        success: function (data) {
            console.log(data['embed_url'])
            $('.video_deets').css('display', 'block');

            if ((data['status'] == 1) || (data['status'] == 2)) {
                
                $('.iframe_container').html("<iframe src=" + data['embed_url'] + "></iframe>")

                if (data['status'] == 1) {
                    $('#status').append("Video parsed successfully")
                    $('#status').addClass('alert-success')
                } else {
                    $('#status').append("This video was searched recently. Extracting data from database")
                    $('#status').addClass('alert-warning')
                }

                $('#video_title').html(data['title'])
                $('#video_views').html(data['views'])
                $('#video_description').html(data['description'])
                $('#video_pdate').html(data['date_published'])
                $('#video_likes').html(data['likes'])
                $('#comments_count').html(data['comments_count'])
                $('#channel_name').html(data['channel']['name'])
                $('#channel_name').attr("href", data['channel']['url'])
                // $('#channel_subscribers').html(data['channel']['subscribers'])
                $('.total_tags').html(data['tags'].length);
                $('#status').css({ 'margin': '20px 0px 0px 0px' });
                $('.form_container').css({ 'height': '10vh', 'padding': '20px 0px 0px 0px' });
                $('.youtube_link_input').css('height', '60px');
                $('.youtube_submit_button').css({ 'font-size': '0.5em !important' })
                $('.intro_container').css('display', 'none');

                if (data['comments'] != 'none') {
                    for (i = 0; i < data['comments'].length; i++) {
                        var comment_author = "<p class='fst-italic'>" + data['comments'][i]['author'] + "</p>"
                        var comment_post_time = "<a class='text-decoration-underline'>" + data['comments'][i]['time'] + "</a>"
                        var comment_votes = "<p>" + data['comments'][i]['votes'] + " likes" + "</p>"
                        var comment_text = "<p class='fw-bold'>" + data['comments'][i]['text'] + "</p>"
                        var complete = comment_text + comment_author + comment_votes + comment_post_time
                        var to_append = "<li class='list-group-item'>" + complete + "</li>"
                        $('.comments_list').append(to_append)
                    }
                    $('#top_comment_count').html(data['comments'].length)
                }

                else {
                    $('#top_comment_count').html(0)
                }

                // prediction stuff
                if (data['prediction'] == 'negative') {
                    $('.prediction_title').html('This is a negative video')
                    $('.prediction_container').addClass('negative_container')
                    $('.accordion-button').addClass('negative_container')
                    $('#meta_table_heading').addClass('table-danger')
                    $('#feature_table_heading').addClass('table-danger')
                    $('.total_tags').addClass('bg-danger')
                    $('.prediction_title').addClass('text-danger')

                    for (i = 0; i < data['tags'].length; i++) {
                        $('#video_tags').append("<small class='btn btn-outline-danger tag'>" + data['tags'][i] + "</small>")
                    }
                }

                else if (data['prediction'] == 'neutral') {
                    $('.prediction_title').html('This is a neutral video')
                    $('.prediction_container').addClass('neutral_container')
                    $('.accordion-button').addClass('neutral_container')
                    $('#meta_table_heading').addClass('table-warning')
                    $('#feature_table_heading').addClass('table-warning')
                    $('.total_tags').addClass('bg-warning')
                    $('.prediction_title').addClass('text-warning')

                    for (i = 0; i < data['tags'].length; i++) {
                        $('#video_tags').append("<small class='btn btn-outline-warning tag'>" + data['tags'][i] + "</small>")
                    }
                }

                else {
                    $('.prediction_title').html('This is a positive video')
                    $('.prediction_container').addClass('positive_container')
                    $('.accordion-button').addClass('positive_container')
                    $('#meta_table_heading').addClass('table-success')
                    $('#feature_table_heading').addClass('table-success')
                    $('.total_tags').addClass('bg-success')
                    $('.prediction_title').addClass('text-success')

                    for (i = 0; i < data['tags'].length; i++) {
                        $('#video_tags').append("<small class='btn btn-outline-success tag'>" + data['tags'][i] + "</small>")
                    }
                }

                $('.tag').css("margin", "5px");
                // end of prediction stuff


                var feature_length = Object.keys(data).length
                if (feature_length > 3) {
                    $('#feature_duration').html(data['duration'])
                    $('#feature_age_limit').html(data['age_limit'])
                    $('#feature_view_count').html(data['views'])
                    $('#feature_like_count').html(data['likes'])
                    $('#feature_vl_ratio').html(data['view_like_ratio_smoothed'])
                    $('#feature_is_comments_enabled').html(data['is_comments_enabled'])
                    $('#feature_is_live_content').html(data['is_live_content'])
                    $('#feature_category').html(data['category'])
                    $('#feature_desc_neu').html(data['desc_neu'])
                    $('#feature_desc_neg').html(data['desc_neg'])
                    $('#feature_desc_pos').html(data['desc_pos'])
                    $('#feature_desc_compound').html(data['desc_compound'])
                    $('#feature_comment_neu').html(data['comment_neu'])
                    $('#feature_comment_neg').html(data['comment_neg'])
                    $('#feature_comment_pos').html(data['comment_pos'])
                    $('#feature_comment_compound').html(data['comment_compound'])
                    $('#feature_votes').html(data['votes'])
                    $('#feature_no_comment_binary').html(data['no_comment_binary'])
                }

            } else if (data['status'] == 3) {
                $('#status').append("Video not found")
                $('#status').addClass('alert-danger')
                $('.form_container').css({ 'height': '10vh', 'padding-bottom': '0px' });
                $('.video_embed').css('display', 'none');
                $('.prediction_container').css('display', 'none');
                $('.user_target_select').css('display', 'none');
                $('#video_meta_accordion').css('display', 'none');
            }
        }
    })

    return false;
}

$(function () {
    $('#youtube_link_form').submit(youtube_link_form_submit);
})

$(document).ready(function () {
    $(window).on('load', function () {
        $('#ackModal').modal('show');
    });
})

