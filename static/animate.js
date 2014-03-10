$(document).ready(function(){
    /* using animate.css for all pages */
    $("h2").mouseover(function(){
        $(this).addClass("animated bounceInRight");
    });
    $("li").mouseenter(function(){
        $(this).addClass("animated hinge");
    });
    /*$("li").mouseleave(function(){
        $(this).removeClass("animated hinge");
    });*/
    $("#footer").mouseover(function(){
        $(this).addClass("animated shake");
    });
    /* messages animate for user.html and admin.html */
    /* 不起作用，可能因为不能同时执行自定义的 javascript 验证程序和这里的程序 */
    /*$("#user_submit").click(function(){
        $("#mess_oldpass").fadeIn("slow");
        $("#mess_newpass1").fadeIn("slow");
        $("#mess_newpass2").fadeIn("slow");
    });
    $("#admin_submit").click(function(){
        $("#mess_cmd").fadeIn("slow");
    });*/
});
