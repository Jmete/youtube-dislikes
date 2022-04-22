$(document).ready(function () {
    $('#part1_dropdown').on('change', function() {
        $.ajax({
            url: $(this).attr('action'),
            data: {'part1_dropdown': this.value},

            success: function (data) {
                $('.part1_graph').html(data['html_data'])
            }
        })
    })

    $('#part2_dropdown').on('change', function() {
        $.ajax({
            url: $(this).attr('action'),
            data: {'part2_dropdown': this.value},

            success: function (data) {
                $('.part2_graph').html(data['html_data'])
            }
        })
    })

    $('#part3_dropdown').on('change', function() {
        $.ajax({
            url: $(this).attr('action'),
            data: {'part3_dropdown': this.value},

            success: function (data) {
                $('.part3_graph').html(data['html_data'])
            }
        })
    })
})