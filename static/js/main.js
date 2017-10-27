function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
      }
    }
  }
  return cookieValue;
}


function moveSelectItems(from, to) {
  var from = document.getElementById(from)
  var to = document.getElementById(to)
  while(from.selectedIndex != -1) {
    to.appendChild(from.options[from.selectedIndex])
  }
}


function selectAllOptions() {
  $("#selected option").each(function() {
    $(this).prop("selected", true);
  });
}


function selectAllDataItems() {
  is_checked = $(this).prop("checked");
  $(".data-item").each(function() {
    $(this).prop("checked", is_checked);
  })
}


function deleteMultiDataItems() {
  var data_items = [];
  $("input:checked.data-item").each(function() {
    data_items.push($(this).attr("value"));
  });
  if (confirm("确认删除?")) {
    $.ajax({
      async: false,
      type: "DELETE",
      url: $(this).prop("href"),
      contentType: "application/json",
      headers: {"X-CSRFToken": getCookie('csrftoken')},
      data: JSON.stringify({
        "data_items": data_items,
      }),
      success: function(result, status, xhr) {
        window.location.reload();
        alert(result);
      }
    });
  }
}


function deleteSingleDataItem() {
  if (confirm("确认删除?")) {
    $.ajax({
      async: false,
      type: "POST",
      url: $(this).prop("href"),
      headers: {"X-CSRFToken": getCookie('csrftoken')},
      success: function(result, status, xhr) {
        window.location.reload();
        alert(result);
      }
    });
  }
}


function notifyUserByEmail() {
  $.ajax({
    async: false,
    type: "POST",
    url: $(this).prop("href"),
    headers: {"X-CSRFToken": getCookie('csrftoken')},
    success: function(result, status, xhr) {
      alert(result);
    }
  });
}


function getAssetSpecifyByType() {
  $("#unselected").empty();
  var type = $("#asset-linkage option:selected").attr("value");
  $.ajax({
    async: false,
    type: "GET",
    url: "/asset/asset/search/",
    data: {"type": type},
    success: function(result, status, xhr) {
      for (var i=0; i<result.length; i++) {
        $("#unselected").append("<option value='" + result[i].pk + "'>" + result[i].label + "</option>");
      }
    }
  });
}


function getAuditExecuteDetail() {
  $(".modal-body").empty();
  $.ajax({
    async: false,
    type: "GET",
    url: $(this).attr("data-url"),
    success: function(result, status, xhr) {
      for (var i=0; i<result.length; i++) {
        $(".modal-body").append('<div>' + result[i].time + '&nbsp;&nbsp;' + result[i].command + '</div>');
      }
    }
  });
}


function killAuditExecuteProgress() {
  $.ajax({
    async: false,
    type: "POST",
    url: $(this).attr("data-url"),
    headers: {"X-CSRFToken": getCookie('csrftoken')},
    success: function(result, status, xhr) {
      window.location.reload();
    }
  });
}


$(document).ready(function() {
  $(".data-items-switch").click(selectAllDataItems);
  $(".delete-multi-data").click(deleteMultiDataItems);
  $(".delete-single-data").click(deleteSingleDataItem);
  $(".email-notity").click(notifyUserByEmail);
  $(".with-multi-select").click(selectAllOptions);
  $(".get-audit-execute-detail").click(getAuditExecuteDetail);
  $(".kill-audit-execute-progress").click(killAuditExecuteProgress);
  $(".add-select-option").click(function() {
    moveSelectItems("unselected", "selected");
  });
  $(".remove-select-option").click(function() {
    moveSelectItems("selected", "unselected");
  });
  $("#asset-linkage").change(getAssetSpecifyByType);
});
