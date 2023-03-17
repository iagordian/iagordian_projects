
//Реакция на нажатие кнопки в правом боковом меню - изменение внутреннего текста
var absent_btns = document.getElementsByClassName('setting_value_btn')

for (i = 0; i < absent_btns.length; i++) {

    absent_btns[i].onclick = function() {

        if (this.innerText != '✓') {this.innerText = '✓'} else {this.innerText = ''};
    }
}

//Реакция на изменение в ячейке расписания - отправка HTTP запроса на сервер для сохранения
var timetable_cells = document.getElementsByClassName('timetable_cell')

for (i = 0; i < timetable_cells.length; i++) {

    timetable_cells[i].onchange = function() {

        var req = new XMLHttpRequest();
        var value = this.value;
        var tutor_id = this.id.split('_')[0];
        var lesson_num = this.id.split('_')[1];

        var data = {
        'value': value,
        'tutor_id': tutor_id,
        'lesson_num': lesson_num,
        }

        req.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        resp = jsonify(this.responseText)
        document.getElementById("feedbackEl").innerHTML = resp.status;
        }}

        req.open("POST", "/save_cell", true);
        req.setRequestHeader("Content-type", "application/json");
        req.send(JSON.stringify(data));
        }
}


// Вызов окошка регистрации пользователя при нажатии на соответствующую кнопку
document.getElementById('to_reg_btn').onclick = function() {
    document.getElementById('grey').style.display = '';
    document.getElementById('log_div').style.display = '';
}

// Переключение между окнами регистрации и авторизации
document.getElementById('reg_btn').onclick = function() {

    document.getElementById('log_div').style.display = 'none';
    document.getElementById('reg_div').style.display = '';
}

document.getElementById('enter_btn').onclick = function() {

    document.getElementById('log_div').style.display = '';
    document.getElementById('reg_div').style.display = 'none';
}

// Свертывание окошка регистрации при нажатии на соответствующую кнопку
var exit_btns = document.getElementsByClassName('exit_btn')
var reg_windows = document.getElementsByClassName('reg_window')

for (i = 0; i < exit_btns.length; i++) {

    exit_btns[i].onclick = function() {

        document.getElementById('grey').style.display = 'none';

        for (j = 0; j < reg_windows.length; j++) {
            reg_windows[j].style.display = 'none';
        }
    }
}
