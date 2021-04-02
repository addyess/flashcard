function update_timer(ansBox, wait_time){
    var page_wait = {{ args.wait_time }};
    var disable_timer = (page_wait == 0 || {{ "true" if not args.no_hints and card.tries > 0 else "false" }});
    var yellow = Math.ceil(2 * page_wait / 3) + 1;
    var red = Math.ceil(page_wait / 3) + 1;
    var timeoutBox = $("#timeout");
    timeoutBox.html(wait_time);

    if (page_wait && wait_time == 0){
        var ans = $('input[name ="ans"]');
        ans.hide().val("time is up");
        $("#card").submit();
    }

    var timeoutElem = $("#timeout-row");
    if ( !disable_timer && wait_time > 0 ){
        timeoutElem.show();
        if (wait_time < yellow){ timeoutBox.css("background-color", "yellow"); }
        if (wait_time < red){ timeoutBox.css("background-color", "red"); }
        setTimeout(function(){
            wait_time -= 1;
            update_timer(ansBox, wait_time);
        }, 1000);
    }
}

$(document).ready(function(){
    var buttons = $(":button");
    var ans = "{{ card.correct_ans }}";
    var ansBox = $(":text");
    var card = $("#card");
    function check_length() {
        this.value = this.value.replace(/[^0-9\.]/g,'');
        if ( this.value.length >= ans.length ) {
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