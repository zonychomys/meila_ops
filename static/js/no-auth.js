function refreshCaptcha() {
  $.getJSON("/captcha/refresh/", {}, function(result) {
    $("input[name='captcha_0']").val(result.key);
    $("#captchaRefresh").attr("src", result.image_url);
  });
}


$(function() {
  /* particlesJS.load(@dom-id, @path-json, @callback (optional)); */
  particlesJS.load('particles-js', '/static/assets/particles.json', function() {
    console.log('callback - particles.js config loaded');
  });
  $("#captchaRefresh").click(refreshCaptcha);
})
