// --------------- Loading ---------------
const startLoading = () => {
  document.getElementById("loading").style.display = "flex";
};
const stopLoading = () => {
  document.getElementById("loading").style.display = "none";
};
// --------------- phone number validator ---------------
const validatePhoneNo = (e, obj) => {
  var x = e.which || e.keycode;
  if (x >= 48 && x <= 57 && obj.value.length < 10) return true;
  else return false;
};
// --------------- pin code validator ---------------
const validatePinCode = (e, obj) => {
  var x = e.which || e.keycode;
  if (x >= 48 && x <= 57 && obj.value.length < 6) return true;
  else return false;
};
// -------------------- Notifications --------------------
const messages = document.getElementById("messages").children;
const total = messages.length;
let message;
for (let i = 0; i < total; i++) {
  message = messages[i].innerHTML.split("||||");
  if (message[0] === "success") alertify.success(message[1]);
  else if (message[0] === "error") alertify.error(message[1]);
}
// -------------------- Alerts --------------------
const showAlert = (head, msg, field = null) => {
  alertify
    .alert(msg, function () {
      setTimeout(() => {
        if (field) uname.focus();
      }, 10);
    })
    .setHeader("<em> " + head + " </em> ");
};
// -------------------- show/hide selectors --------------------
const show = (selectors) => {
  const elements = document.querySelectorAll(selectors);
  elements.forEach((element) => {
    element.style.display = "block";
  });
};
const hide = (selectors) => {
  const elements = document.querySelectorAll(selectors);
  elements.forEach((element) => {
    element.style.display = "none";
  });
};
// --------------- time zons ---------------
const fromatToDateTime = (datetimeStr) => {
  return Date.parse(datetimeStr.split('.')[0]).add({ hours: 5, minutes: 30 }).toString("ddd, MMM d, yyyy HH:mm:ss");
}
const formatToDate = (datetimeStr) => {
  return Date.parse(datetimeStr.split('.')[0]).add({ hours: 5, minutes: 30 }).toString("dd-MMM-yyyy");
}
// --------------- button loading ---------------
const showBtnLoading = (btn) => {
  if (!btn) return;
  btn.setAttribute("data-html", btn.innerHTML);
  btn.setAttribute("disabled", true);
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
};
const hideBtnLoading = (btn) => {
  if (!btn) return;
  btn.innerHTML = btn.getAttribute("data-html");
  btn.removeAttribute("disabled");
};
// --------------- icon button loading ---------------
const showIconBtnLoading = (btn) => {
  if (!btn) return;
  btn.setAttribute("data-html", btn.innerHTML);
  btn.setAttribute("disabled", true);
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
};
const hideIconBtnLoading = (btn) => {
  if (!btn) return;
  btn.innerHTML = btn.getAttribute("data-html");
  btn.removeAttribute("disabled");
};
// --------------- text copy ---------------
const copyToClipboard = (text) => {
  const copyAreaId = `copy-${new Date().getTime()}`;
  document.querySelector('body').insertAdjacentHTML("beforeend", `<textarea style="display: none" id="${copyAreaId}"></textarea>`);
  const copyArea = document.getElementById(copyAreaId);
  copyArea.value = text;

  // Select the text field
  copyArea.select();
  copyArea.setSelectionRange(0, 99999); // For mobile devices

   // Copy the text inside the text field
  navigator.clipboard.writeText(copyArea.value);

  // Alert the copied text
  alertify.success("Copied to clipboard successfully.");

  // removing element from dom
  copyArea.remove();
}
// --------------- popups ---------------
const showFlexPopup = (id) => {
  document.getElementById(id).style.display='flex';
}
const hideFlexPopup = (id) => {
  document.getElementById(id).style.display='none';
}
// --------------- share ---------------
const sharePost = async (postId) => {
  startLoading();
  const result = await getFromServer(`/post/${postId}/get-post-url`);
  stopLoading();
  if (result.status) openSharePopup("Share Post", result.data.post_url)
  else alertify.error(result.msg);
}
const openSharePopup = (heading, url) => {
  const link = `${window.location.origin}${url}`;

  document.getElementById('share-head').innerHTML = heading;
  document.getElementById('share-w').href = `whatsapp://send?text=${link}`;
  document.getElementById('share-m').href = `mailto:?subject=schoolistan Post&body=Check out this post on site ${link}`;
  document.getElementById('share-link').innerHTML = link;
  document.getElementById('share-copy-btn').setAttribute("onclick", `copyToClipboard('${link}')`);

  document.getElementById('share-popup').style.display='flex';
}
const closeSharePopup = () => {
  document.getElementById('share-head').innerHTML = "Share";
  document.getElementById('share-w').href = "";
  document.getElementById('share-m').href = "";
  document.getElementById('share-link').innerHTML = "";
  document.getElementById('share-copy-btn').removeAttribute("onclick", "");

  document.getElementById('share-popup').style.display='none';
}
