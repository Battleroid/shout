$(document).ready(function () {
    var cont = $('#megaphone');
    cont.masonry({
        itemSelect: '.panel',
        'gutter': 15
    });
    $("input#shout-submit").click(function () {
        $("form#shout-form").submit();
    });
    $(".alert").each(function (index) {
        $(this).delay(2000 + (index * 1000)).slideUp(500);
    })
});
