function update_timer(ansBox, wait_time){
    var yellow = Math.ceil(2 * {{ args.wait_time }} / 3) + 1;
    var red = Math.ceil({{ args.wait_time }} / 3) + 1;
    var timeoutElem = $("#timeout-row");
    if (wait_time >= 0 ){
        var timeoutBox = $("#timeout");
        timeoutBox.html(wait_time);
        if (wait_time < yellow){ timeoutBox.css("background-color", "yellow"); }
        if (wait_time < red){ timeoutBox.css("background-color", "red"); }
        timeoutElem.show();
        setTimeout(function(){
            wait_time -= 1;
            if (wait_time == 0){
                var ans = $('input[name ="ans"]');
                ans.val("time is up");
                $("#card").submit();
            } else {
                update_timer(ansBox, wait_time);
            }
        }, 1000);
    } else {
        timeoutElem.hide();
    }
}

$(document).ready(function(){
    var buttons = $(":button");
    var ans = "{{ ans }}";
    var ansBox = $(":text");
    var card = $("#card");
    function check_length() {
        if ( ansBox.val().length >= ans.length ) {
            card.submit();
        }
    }
    function btnClicked(btn){
        $(btn.currentTarget).focusout();
        var value = btn.currentTarget.value;
        ansBox.val(parseInt(ansBox.val() + value));
        check_length();
    }
    buttons.click(btnClicked);
    ansBox.keyup(check_length).focus();
    card.submit(function(event){
        ansBox.css("color", "white");
        ansBox.css("background-color", ansBox.val() == ans ? "green" : "red");
    })

    update_timer(ansBox, {{ args.wait_time }});
})