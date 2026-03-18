// ---------- constants ----------
const existingIds = [];
var postLoading = false;
var bannerList = [];
var bannerIndex = 0;
var bannerCount = 0;
var postIndex = 0;
const dataBox = document.getElementById("data-box");
const currUrl = window.location.pathname;
const loadMorePostBtn = document.getElementById('load-more-post-btn');
const dataLoading = document.getElementById("data-loading");
// ---------- sliders ----------
function changePostSlide(btn, post_id, attachNo) {
  const slider = document.getElementById("slider-" + post_id);
  slider.setAttribute("data-no", attachNo);
  slider.style.transform = `translate3d(-${attachNo * 100}%, 0px, 0px)`;
  const allDots = btn.parentNode.querySelectorAll('span.dot');
  allDots.forEach(dot => dot.classList.remove('active'));
  btn.classList.add('active');
}
function postSlideNext(postId) {
  const slider = document.getElementById("slider-" + postId);
  let counter = parseInt(slider.getAttribute("data-no"));
  if (counter >= slider.childElementCount - 1) {
    return;
  }
  counter++;
  slider.setAttribute("data-no", counter);
  slider.style.transform = `translate3d(-${counter * 100}%, 0px, 0px)`;
  
  const currDot = document.getElementById(`dot-${postId}-${counter}`);
  const allDots = currDot.parentNode.querySelectorAll('span.dot');
  allDots.forEach(dot => dot.classList.remove('active'));
  currDot.classList.add('active');
}
function postSlideBack(postId) {
  const slider = document.getElementById("slider-" + postId);
  let counter = parseInt(slider.getAttribute("data-no"));
  if (counter <= 0) {
    return;
  }
  counter--;
  slider.setAttribute("data-no", counter);
  slider.style.transform = `translate3d(-${counter * 100}%, 0px, 0px)`;

  const currDot = document.getElementById(`dot-${postId}-${counter}`);
  const allDots = currDot.parentNode.querySelectorAll('span.dot');
  allDots.forEach(dot => dot.classList.remove('active'));
  currDot.classList.add('active');
}
// ---------- poster loading ----------
const loadBanners = async () => {
  const result = await getFromServer(bannerUrl);
  if (result.status) {
    bannerList = result.data.banners;
    bannerCount = result.data.banners.length;
  } else alertify.error(result.msg);
}
if(typeof bannerUrl != 'undefined' && bannerUrl) {
  loadBanners();
}
// ---------- post loading ----------
async function loadShorts() {
  if(postLoading) return;
  postLoading = true;
  // showBtnLoading(btn);
  dataLoading.style.display = 'block';
  loadMorePostBtn.style.display = 'none';
  const result = await getFromServer(`${posts_url}&existing_ids=${existingIds.toString()}`);
  dataLoading.style.display = 'none';
  loadMorePostBtn.style.display = 'inline';
  // hideBtnLoading(btn);
  if (result.status) {
    result.data.forEach((row) => {
      // console.log(row.attachments);
      postIndex++;
      existingIds.push(row.id);
      const attachmentCount = row.attachments.length;
      let attachments, slider_dots, gridColumm, dotAct, attachClick;
      attachments = slider_dots = gridColumm = dotAct = attachClick = "";
      for (let i = 0; i < attachmentCount; i++) {
        const attach = row.attachments[i];
        if(i == 0) {
          dotAct = 'active';
          attachClick = "";
        } else {
          dotAct = "";
          attachClick = row.locked ? 'onclick="gotToCourses()"' : '';
        }
        if (attach.type == 1) {
          attachments += `<div class="attach" ${attachClick}><img src="${mediaUrl}${attach.attachment}" alt="Attachment" /></div>`;
        } else if (attach.type == 2) {
          attachments += `<div class="attach" ${attachClick}>
            <video width="100%" height="" controls controlsList="nodownload">
              <source src="${mediaUrl}${attach.attachment}" type="video/mp4" />
            </video>
          </div>`;
        } else if (attach.type == 3) {
          attachments += `<div class="attach" ${attachClick}>
            <div class="iframe-box">
              <iframe src="https://www.youtube.com/embed/${attach.attachment}" allowfullscreen="allowfullscreen" frameborder="0"></iframe>
            </div>
          </div>`;
        }
        slider_dots += `<span class="dot ${dotAct}" id="dot-${row.id}-${i}" onclick="changePostSlide(this, ${row.id}, ${i})"></span>`;
        gridColumm += ' 100%';
      }
      // preparing post html content to append in dom
      const dataHtml = `
      <div class="shortpost" id="${row.id}">
        <div class="head">
          ${row.premium ? '<span title="premium"><i class="fa-solid fa-crown" ></i></span>' : ''}
          ${row.featured ? '<span title="Featured"><i class="fa-solid fa-award"></i></span>':''}
          <span style="flex:1;"></span>
          ${ is_teacher || row.user_id == user_id   ? `<a title="Delete" onclick="deletePost(${row.id})" href="javascript:void(0);"><i class="fa-solid fa-trash"></i></a>&nbsp;<a title="Edit" href="/post/post/${row.id}/edit?next=${currUrl}"><i class="fa-solid fa-pen-to-square"></i></a>` : ""}
          ${row.locked ? '<a href="/courses" title="Locked" style="color: red;"><i class="fa-solid fa-lock"></i></a>':''}
        </div>
        <div class="body">
          <div class="media">
            ${attachments ?
              `<div class="slider" style="grid-template-columns:${gridColumm};" id="slider-${row.id}" data-no="0">${attachments}</div>
              <div class="slide-btns">
                <button class="back" onclick="postSlideBack(${row.id})"><i class="fa-solid fa-caret-left"></i></button>
                <button class="next" onclick="postSlideNext(${row.id})"><i class="fa-solid fa-caret-right"></i></button>
              </div>
              `
              : ''}
          </div>
          ${slider_dots ? `<div class="media-dots">${slider_dots}</div>` : ''}
          ${row.text ? `<div class="description para-box" id="desc-${row.id}">${row.text}</div>` : ""}
          ${row.text? '<button onclick="hideShowDec(' + row.id + ', this)">View More</button>': ""}
          <button onclick="showTranscript(${row.id})" style="float: right;">Transcript</button>
        </div>
        ${row.title ? `<p class="title">${row.title}</p>` : ""}
        <div class="post-by">
          <a href="/account/${row.username}" style="display: contents;" target="_blank">
            <img src="${userPic}" alt="Avatar" />&nbsp;${row.username}
          </a>
          <p style="flex: 1"></p>
          <p>${formatToDate(row.created_on)}</p>
        </div>
        <div class="post-b-nav" >
          <button data-liked="${row.liked}" class="${row.liked > 0 ? "active": ""}" onclick="postlike(${row.id}, this)">
            <i class="fa-solid fa-thumbs-up"></i> <span id="likecount-${row.id}">${row.likes}</span>  like
          </button>
          <button onclick="hideShowComment(${row.id})" >
            <i class="fa-solid fa-comment"></i> <span id="commentCount-${row.id}">${row.comments}</span> comment
          </button>
          <button onclick="sharePost(${row.id});"><i class="fa-solid fa-share-nodes"></i> shere</button>
        </div>
        <div class="comments" id="commbox-${row.id}" style="display: none;">
          <div style="display: flex; align-items: center">
            <textarea name="text" id="comm-${row.id}" style="flex: 1" class="input" rows="2"></textarea>
            &nbsp;
            <div>
              <button class="btn pri" type="submit" onclick="postcomment(${row.id}, this)">
                  <i class="fa-solid fa-floppy-disk"></i>
              </button>
            </div>
          </div>
          <br />
          <div class="comlist" id="comlist-${row.id}" style="display: block;"></div>
        </div>
        <div class="transcript" id="transcript-${row.id}" style="display: none; white-space: pre-line">
          ${row.transcript ? row.transcript : '<p style="text-align: center;">No Transcript</p>'}
        </div>
      </div>
      `;
      dataBox.insertAdjacentHTML("beforeend", dataHtml);
      // adding slides effect in post for mobile and babs
      if(attachments != '') {
        handleHzSwipe(document.getElementById(`slider-${row.id}`), () => postSlideBack(row.id), () => postSlideNext(row.id));
      }
      // adding banners between the post
      if(bannerCount > 0 && postIndex % 3 == 0) {
        bannerIndex++;
        if(bannerIndex >= bannerCount) bannerIndex = 0;
        const bannerData = bannerList[bannerIndex];
        const dataHtml2 = `<a class="ads-banner" href="${bannerData[2]}"><img src="${mediaUrl}${bannerData[3]}" alt="${bannerData[1]}" /></a>`;
        dataBox.insertAdjacentHTML("beforeend", dataHtml2);
      }
    });
  } else {
    alertify.error(result.msg);
  }
  postLoading = false;
}
const gotToCourses = () => {
  window.location.href = "/courses";
}
// ---------- hide show description ----------
function hideShowDec(id, btn) {
  const desc = document.getElementById(`desc-${id}`);
  if(desc.getAttribute('data-expanded') == '1') {
    desc.style.maxHeight = `360px`;
    desc.removeAttribute('data-expanded');
    btn.innerHTML="View More"
  } else {
    desc.style.maxHeight = "max-content";
    desc.setAttribute('data-expanded', '1');
    btn.innerHTML="View Less"
  }
}
// ---------- post delete ----------
async function deletePost(id) {
  const decision = confirm("Do you really want delete this Post");
  if (decision) {
    const result = await postToServer(`/post/post/${id}/delete`);
    if (result.status) {
      alertify.success(result.msg);
      document.getElementById(id).remove();
    } else {
      alertify.error(result.msg);
    }
  }
}
// ---------- post like ----------
async function postlike(id, element) {
  if(user_id) {
    const liked = parseInt(element.dataset.liked);
    showIconBtnLoading(element);
    const result = await postToServer(`/post/post/${id}/like`, { liked: liked });
    hideIconBtnLoading(element);
    if (result.status) {
      document.getElementById(`likecount-${id}`).innerHTML = result.data.count;
      if (result.data.liked) {
        element.classList.add("active");
        element.dataset.liked = 1;
      } else {
        element.classList.remove("active");
        element.dataset.liked = 0;
      }
      // alertify.success(result.msg);
    } else {
      alertify.error(result.msg);
    }
  } else {
    window.location.href = `/login?next=${window.location.pathname}`;
  }
}
// ---------- post comment ----------
async function postcomment(id, btn) {
  if(user_id) {
    const input = document.getElementById(`comm-${id}`);
    if (input.value.trim() == "") {
      alertify.error("Please enter comment");
      return;
    }
    showIconBtnLoading(btn);
    input.setAttribute('disabled', true);
    const result = await postToServer(`/post/post/${id}/comment`, {
      comment: input.value,
    });
    hideIconBtnLoading(btn);
    input.removeAttribute('disabled');
    if (result.status) {
      document.getElementById(`commentCount-${id}`).innerHTML = result.data.count;
      // alertify.success(result.msg);
      input.value = "";
      renderComments(id);
    } else {
      alertify.error(result.msg);
    }
  } else {
    window.location.href = `/login?next=${window.location.pathname}`;
  }
}
// ---------- post comment hide show ----------
const hideShowComment = (id) => {
  const combox = document.getElementById(`commbox-${id}`);
  if (combox.style.display == "none") {
    combox.style.display = "block";
    renderComments(id);
  } else {
    combox.style.display = "none";
  }
}
const showTranscript = (id) => {
  const transcript = document.getElementById(`transcript-${id}`);
  if (transcript.style.display == "none") transcript.style.display = "block";
  else transcript.style.display = "none";
}
// ---------- post comments rendering ----------
async function renderComments(id) {
  const combox = document.getElementById(`commbox-${id}`);
  const comlist = document.getElementById(`comlist-${id}`);
  comlist.innerHTML = `<div style="text-align: center; margin-bottom: 20px;"><i class="fas fa-spinner fa-spin"></i></div>`;
  const result = await getFromServer(`/post/post/${id}/comments`);
  comlist.innerHTML = "";
  if (result.status) {
    document.getElementById(`commentCount-${id}`).innerHTML =
      result.data.comments.length;
    result.data.comments.forEach((element) => {
      // console.log(element)
      dataHtml = `
        <div class="combox">
          <p>${element[1]}</p>
          <b style="text-align: end; display: block">${formatToDate(
            element[2]
          )} | ${element[3]} </b>
          </div>
        </div>
        `;
      comlist.insertAdjacentHTML("beforeend", dataHtml);
    });
  } else {
    alertify.error(result.msg);
  }
}

const loadMorePosts = () => {

}

if(typeof posts_url != 'undefined' && posts_url) {
  loadShorts();

  // code for scroll up
  var lastScrollTop = 0;
  // element should be replaced with the actual target element on which you have applied scroll, use window in case of no target element.

  // window.addEventListener(
  //   "scroll",
  //   function () {
  //     var st = window.pageYOffset || document.documentElement.scrollTop;

  //     if (st > lastScrollTop) {
  //       // Do scroll down code

  //       // console.log(st);
  //       // console.log("Down");

  //       // code for checking bottom reach or not
  //       if(st >= (document.documentElement.scrollHeight - window.innerHeight)) {
  //         loadShorts();
  //         // console.log("reached at bottom.");
  //       }
  //     } else {
  //       // Do scroll up code

  //       // console.log("Up");
  //     }

  //     lastScrollTop = st <= 0 ? 0 : st; // For Mobile or negative scrolling
  //   },
  //   false
  // );

}

loadMorePostBtn.onclick = loadShorts;
