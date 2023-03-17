
// Появление расписания тьютора при нажатии на соответствующую кнопку
var timetable_btns = document.getElementsByClassName('setting_tm_btn')

for (i = 0; i < timetable_btns.length; i++) {

    timetable_btns[i].onclick = function() {
        document.getElementById(this.value).style.display = '';
        document.getElementById('grey').style.display = '';

    }
}

// Свертывание расписания тьютора при нажатии на соответствующую кнопку
var exit_btns = document.getElementsByClassName('exit_btn')

for (i = 0; i < exit_btns.length; i++) {

    exit_btns[i].onclick = function() {
        document.getElementById(this.value).style.display = 'none';
        document.getElementById('grey').style.display = 'none';
    }
}

// Переключение актуальной таблицы настроек и отправление на сервер HTTP запроса о произошедших изменениях
document.getElementById('settings_choice').onchange = function() {
    var value = this.value;

    if (value == "student")
            {document.getElementById('tutors_div').style.display = 'none';
            document.getElementById('students_div').style.display = '';
            document.getElementById('plugs_div').style.display = 'none';}

    else
        if (value == "tutor")
            {document.getElementById('tutors_div').style.display = '';
            document.getElementById('students_div').style.display = 'none';
            document.getElementById('plugs_div').style.display = 'none';}
        else
            {document.getElementById('tutors_div').style.display = 'none';
            document.getElementById('students_div').style.display = 'none';
            document.getElementById('plugs_div').style.display = '';}

    var req = new XMLHttpRequest();
    var value = this.value;

    var data = {
    'actual_table': value,
    }

    req.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
    resp = jsonify(this.responseText)
    document.getElementById("feedbackEl").innerHTML = resp.status;
    }}

    req.open("POST", "./change_actual_table", true);
    req.setRequestHeader("Content-type", "application/json");
    req.send(JSON.stringify(data));
}

// Реакция на нажатие кнопки настроек ученика - изменение внутреннего текста кнопки
var comb_btns = document.getElementsByClassName('stud_comb')

for (i = 0; i < comb_btns.length; i++) {

    comb_btns[i].onclick = function() {
        if (this.innerText != '✓') {this.innerText = '✓'} else {this.innerText = ''};
    }
}

// Реакция на изменение настроек расписания - отправление HTTP запроса на сервер с информацией о произошедшем изменении
var setting_attrs = document.getElementsByClassName('setting_attrs')

for (i = 0; i < setting_attrs.length; i++) {

    setting_attrs[i].onchange = function() {

        var req = new XMLHttpRequest();
        var category = this.id.split('_')[0]
        var attribute = this.id.split('_')[1]
        var element_id = this.id.split('_')[2]
        var value = this.value

        var data = {
        'category': category,
        'attribute': attribute,
        'element_id': element_id,
        'value': value
        }

        req.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        resp = jsonify(this.responseText)
        document.getElementById("feedbackEl").innerHTML = resp.status;
        }}

        req.open("POST", "./change_settings", true);
        req.setRequestHeader("Content-type", "application/json");
        req.send(JSON.stringify(data));
    }
}