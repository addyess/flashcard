function remove_row(){
    var row = $(this).closest('tr');
    row.hide(250, complete=function(){row.remove();});
};

function add_card(where){
    var $tr = $(where).closest(".clone");
    var $clone = $tr.clone();
    $tr.after($clone);
    $tr.removeClass("clone");
    $clone.find('.addable').click(click_add);
    $(where).removeClass("addable")
           .addClass("removable")
           .off()
           .click(remove_row)
           .html("-");
    return where;
}
function click_add(){return add_card(this);};

function update(){
    var practice_data = $('.card')
        .map(function(){
            let card = $(this).val();
            let pattern = new RegExp($(this).attr('pattern'));
            if (card =="" || pattern.test(card)){ return card; } else {
                let msg = card + " is not valid"
                alert(msg);
                throw msg;
            }
        })
        .get()
        .filter(word => word != "");

    $.post({
        url:"/update",
        contentType: "application/json",
        data: JSON.stringify({
            practice_data: practice_data,
            repeat: $(".repeat:selected").val(),
            wait_time: parseInt($("#wait_time").val()),
            total: parseInt($("#total").val()),
            no_hints: $("#hints").is(':checked') == false,
            operators: $(".operators:checked").map(function(){return $(this).val()}).get().join(''),
        }),
    });
}

function reveal_range() {
    var val = $(this).val();
    $(this).siblings("label").children("span").html(val)
}

$(document).ready(function(){
    var practice_data = {{ args.practice_data }};
    for (const card of practice_data){
        var row = $(add_card($('.addable'), card)).closest('tr');
        row.find('.card').val(card);
    }
    $(".addable").click(click_add);
    $(".submit").click(update);
    $(".form-range").change(reveal_range)
})