$(document).ready(function () {
    $(document).on("click", "#user_select_positive_button", function(){
        $.ajax({
            url: $(this).attr('action'),
            type: 'GET',

            success: function () {
                $('.user_target_select').css('display', 'none');
            }
        })
    })

    $(document).on("click", "#user_select_negative_button", function(){
        $.ajax({
            url: $(this).attr('action'),
            type: 'GET',

            success: function () {
                $('.user_target_select').css('display', 'none');
            }
        })
    })
})