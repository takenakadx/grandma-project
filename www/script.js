var selected_name_num = 0;
var selected_message_num = 0;
var names = [];
var messages = ["こんにちは","了解","今無理"]
var is_first_page = false;
var interval_function = null;

$(function(){
    to_first_page();
    update_message();
});


function to_first_page(){
    $('#second_page').hide(200);
    $('#first_page').show(200);
    get_names();
    interval_function = setInterval(get_names,10000);
    is_first_page = true;
}
function to_second_page(){
    $('#first_page').hide(200);
    $('#second_page').show(200);
    clearInterval(interval_function);
    is_first_page = false;
}


function get_names(){
    let difference = -names.length;
    $.get('/getdata?type=message',function(data){
        console.log(data)
        names = data
        selected_name_num += (-difference > names.length ? (difference + names.length) : 0);
        update_names();
    })
}
function send_message(){
    let post_message = {to:names[selected_name_num][3],message:messages[selected_message_num]};
    $.get('send_message',post_message).done(function(data){
        console.log(data);
    })
}
function update_to_read(n){
    let postdata = {datetime:names[selected_name_num][0],message:names[selected_name_num][2],userid:names[selected_name_num][3],to:n}
    $.get('update_read',postdata,function(){
        console.log("OK")
    })
}
function say(saytext){
    $.get("say?text="+saytext);
}

function update_names(){
    if(selected_name_num < 0)selected_name_num = 0;
    if(selected_name_num >= names.length)selected_name_num = names.length - 1;
    $('#name_btn').html(names[selected_name_num][1] + '<br>' + names[selected_name_num][2].substr(0,10));
    $('#datetime').text(names[selected_name_num][0]);
    if(names[selected_name_num][5] == "0"){
        $('#new_flag').text("未読");
    }else if(names[selected_name_num][5] == "1"){
        $('#new_flag').text("未返信");
    }else if(names[selected_name_num][5] == "2"){
        $('#new_flag').text("返信済み");
    }
}
function update_message(){
    if(selected_message_num < 0)selected_message_num = 0;
    if(selected_message_num >= messages.length)selected_message_num = messages.length-1;
    $('#message_btn').text(messages[selected_message_num])
}
function move(n){
    if(is_first_page){
        selected_name_num += n;
        update_names();
    }else{
        selected_message_num += n;
        update_message();
    }
}
function to_first(){
    selected_name_num = names.length - 1;
    update_names();
}
function click_name(){
    console.log(names[selected_name_num][2]);
    $('#who').html(names[selected_name_num][1] + "<br>" + names[selected_name_num][2] + '<br>への返信');
    say(names[selected_name_num][1] + "さんからのめっせーじ。" + names[selected_name_num][2]);
    if(names[selected_name_num][5] == "0"){
        update_to_read(1);
    }
    to_second_page();
}
function resay(){
    say(names[selected_name_num][1] + "さんからのめっせーじ。" + names[selected_name_num][2]);
}
function click_message(){
    send_message();
    say("返信しました。");
    update_to_read(2);
    to_first_page();
}