// 设置 processing 的 gif 动画
imgOn = new Image;
imgOn.src = "/static/loading.gif";
// 定义函数：验证 str 是否符合整数格式，正确返回 true 否则返回 false
function isInteger(str){
    var regu = /^[0-9]*[1-9][0-9]*$/;
    return regu.test(str);
}
// 定义表单验证程序
function checkForm(){
    // 计算当前年份
    var now = new Date();
    var nowYear = now.getFullYear();
    // 获取表单提交的数据
    var element = document.getElementById('element').value;
    var site = document.getElementById('site').value;
    var startyear = document.getElementById('startyear').value;
    var endyear = document.getElementById('endyear').value;
    var period = document.getElementById('period').value;
    var startmonth = document.getElementById('startmonth').value;
    var startday = document.getElementById('startday').value;
    var endmonth = document.getElementById('endmonth').value;
    var endday = document.getElementById('endday').value;
    // 开始验证表单，主要是针对 IE 浏览器的验证，部分不支持 HTML5 的情况
    var y = document.getElementById("mess_year");
    var z = document.getElementById("mess_date");
    if (element == "please")
        {document.getElementById("mess_element").innerHTML="请选择要素";return false;}
    else if (site == "please")
        {document.getElementById("mess_site").innerHTML="请选择站点";return false;}
    else if (startyear=="" || endyear=="" || startyear==null || endyear==null)
        {y.innerHTML="请填写起止年份";return false;}
    else if (!isInteger(startyear) || !isInteger(endyear))
        {y.innerHTML="请正确输入年份";return false;}
    else if (startyear < 1951)
        {y.innerHTML="起始年份不能早于1951";return false;}
    else if (endyear > nowYear)
        {y.innerHTML="截止年份不能超出"+now.getFullYear();return false;}
    else if (startyear > endyear)
        {y.innerHTML="起始年份不能晚于截止年份";return false;}
    else if (period == "please")
        {// 验证日期是否输入正确，这里的办法挺好
         var d1 = new Date(startyear, startmonth-1, startday);
         var d2 = new Date(endyear, endmonth-1, endday);
         var S = (d1.getFullYear()==startyear && d1.getMonth()+1==startmonth && d1.getDate()==startday);
         var E = (d2.getFullYear()==endyear && d2.getMonth()+1==endmonth && d2.getDate()==endday);
         if (startmonth==""||startday==""||endmonth==""||endday==""||startmonth==null||startday==null||endmonth==null||endday==null)
            {z.innerHTML="未设置时段或填写不全";return false;}
         else if (!S||!E)
            {z.innerHTML="请正确设置日期";return false;}
         // 输入正确的情况下，显示 processing 的 gif 动画，并向服务器提交表单
         else
            {document.myimg.src=imgOn.src;saveall();return true;}
        }
    // 输入正确的情况下，显示 processing 的 gif 动画，并向服务器提交表单
    else// if (period != "please")
        {document.myimg.src=imgOn.src;saveall();return true;}
}
// 定义 select input radio 元素选项的存取函数
// 其中 select 和 input 处理方式相同，用 getElementById(id).value 存取即可
// 注意 radio 的处理方式，用 getElementsByName(name) 获取的是一个数组
function saveSelectBind(id){
    // 这里用 Bind 表示绑定于 id='h2name'
    var h2name = document.getElementById('h2name').innerHTML;
    var data = document.getElementById(id).value;
    localStorage.setItem(h2name+id,data);
}
function loadSelectBind(id){
    var h2name = document.getElementById('h2name').innerHTML;
    var data = localStorage.getItem(h2name+id);
    if (data == ""||data == null) {data = "please";}
    document.getElementById(id).value = data;
}
function saveSelect(id){
    // 不绑定，所有页面相同
    var data = document.getElementById(id).value;
    localStorage.setItem(id,data);
}
function loadSelect(id){
    var data = localStorage.getItem(id);
    if (data == ""||data == null) {data = "please";}
    document.getElementById(id).value = data;
}
function saveInput(id){
    var data = document.getElementById(id).value;
    localStorage.setItem(id,data);
}
function loadInput(id){
    var data = localStorage.getItem(id);
    if (data == null) {data = "";}
    document.getElementById(id).value = data;
}
// 注意 ByName 的用法不同于 ById，首先写法是 getElements 有 s，其次得到的是一个数组
function saveRadio(name){
    var data = document.getElementsByName(name);
    for (var i=0; i<data.length; i++) {
        if (data[i].checked)
            {var ID = name + i; break;}
    }
    localStorage.setItem(name,ID);
}
function loadRadio(name){
    var ID = localStorage.getItem(name);
    if (ID == null) {ID = name + 0;}
    document.getElementById(ID).checked = true;
}
// 在 checkForm() 中通过验证后，调用 saveall() 保存用户的选项操作
function saveall(){
    saveSelectBind('element');
    var SELECTS = new Array('site','period');
    var RADIOS = new Array('Shape','Line','Color','Data');
    var INPUTS = new Array('startyear','startmonth','startday','endyear','endmonth','endday','labelx','labely');
    for (var i=0; i<SELECTS.length; i++) {saveSelect(SELECTS[i]);}
    for (var i=0; i<RADIOS.length; i++) {saveRadio(RADIOS[i]);}
    for (var i=0; i<INPUTS.length; i++) {saveInput(INPUTS[i]);}
}
// 在 MYTHETEMPLATE.htm 的 body 标签 onload 事件中调用 loadall()
function loadall(){
    loadSelectBind('element');
    var SELECTS = new Array('site','period');
    var RADIOS = new Array('Shape','Line','Color','Data');
    var INPUTS = new Array('startyear','startmonth','startday','endyear','endmonth','endday','labelx','labely');
    for (var i=0; i<SELECTS.length; i++) {loadSelect(SELECTS[i]);}
    for (var i=0; i<RADIOS.length; i++) {loadRadio(RADIOS[i]);}
    for (var i=0; i<INPUTS.length; i++) {loadInput(INPUTS[i]);}
}
