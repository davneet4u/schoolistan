// --------------- query parameters ---------------
const params = new Proxy(new URLSearchParams(window.location.search), {
  get: (searchParams, prop) => searchParams.get(prop),
});
// --------------- post create/edit ---------------
const premium = document.getElementById("premium");
const featured = document.getElementById("featured");
const image = document.getElementById("image");
const video = document.getElementById("video");
const youtube = document.getElementById("youtube");
const youtubeBox = document.getElementById("youtube_box");
const imagesBox = document.getElementById("images_box");
const videosBox = document.getElementById("videos_box");
var postUrl = "/";
const makePremium = (obj) => {
  if (premium.value == "1") {
    premium.value = "";
    obj.classList.remove("active");
  } else {
    premium.value = "1";
    obj.classList.add("active");
  }
};
const makeFeatured = (obj) => {
  if (featured.value == "1") {
    featured.value = "";
    obj.classList.remove("active");
  } else {
    featured.value = "1";
    obj.classList.add("active");
  }
};
const addYoutubeLink = (obj) => {
  youtube.value = "";
  if (obj.classList.contains("active")) {
    obj.classList.remove("active");
    youtubeBox.style.display = "none";
    youtube.removeAttribute("required");
  } else {
    obj.classList.add("active");
    youtubeBox.style.display = "flex";
    youtube.focus();
    youtube.setAttribute("required", true);
  }
};
const addImage = (obj) => {
  image.click();
};
const changeImages = (obj) => {
  imagesBox.innerHTML = "";
  if (obj.files && obj.files[0]) {
    const fileCount = obj.files.length;
    for (let i = 0; i < fileCount; i++) {
      let reader = new FileReader();
      reader.readAsDataURL(obj.files[i]);
      reader.onload = (e) => {
        imagesBox.insertAdjacentHTML(
          "beforeend",
          `<img src="${e.target.result}" />`
        );
      };
    }
  }
};
const addVideo = (obj) => {
  video.click();
};
const changeVideos = (obj) => {
  videosBox.innerHTML = "";
  if (obj.files && obj.files[0]) {
    const fileCount = obj.files.length;
    for (let i = 0; i < fileCount; i++) {
      let reader = new FileReader();
      reader.readAsDataURL(obj.files[i]);
      reader.onload = (e) => {
        videosBox.insertAdjacentHTML(
          "beforeend",
          `<video width="" height="150px" controls>
            <source src="${e.target.result}" type="video/mp4" />
          </video>`
        );
      };
    }
  }
};
const afterTitleBlured = (titleIn) => {
  const metaDesc = document.getElementById("meta_description");
  metaDesc.value = metaDesc.value.trim();
  titleIn.value = titleIn.value.trim();
  if(metaDesc.value == '' && titleIn.value != '') metaDesc.value = titleIn.value;
  metaDesc.focus();
}
var attachementList = [];
var attachCounter = 0;
const fileUploadProgress = document.getElementById("file-upload-progress");
const uploadPost = async(form) => {
  const youtubeValue = youtube.value.trim();
  if (youtubeValue != "") {
    if (youtubeValue.includes("youtube.com/watch?v=")) {
      // for youtube video
      const temp = youtubeValue.split("youtube.com/watch?v=");
      youtube.value = temp[temp.length - 1];
    } else if (youtubeValue.includes("youtube.com/embed/")) {
      // for youtube video
      const temp = youtubeValue.split("youtube.com/embed/");
      youtube.value = temp[temp.length - 1];
    } else if (youtubeValue.includes("https://youtu.be/")) {
      // for youtube video
      const temp = youtubeValue.split("https://youtu.be/");
      youtube.value = temp[temp.length - 1];
    } else if (youtubeValue.includes("youtube.com/shorts/")) {
      // for youtube short
      const temp = youtubeValue.split("youtube.com/shorts/");
      youtube.value = temp[temp.length - 1];
    } else {
      alert("Entered youtube url is not valid.");
      return false;
    }
  }
  youtube.setAttribute("readonly", true);
  // form.submit();
  showBtnLoading(document.getElementById('submit-btn'));
  const formData = new FormData();
  formData.append("text", tinymce.get("description").getContent());
  formData.append("transcript", document.getElementById("transcript").value.trim());
  formData.append("title", document.getElementById("title").value.trim());
  formData.append("meta_description", document.getElementById("meta_description").value.trim());
  if(is_teacher) {
    formData.append("categories", document.getElementById("categories").value);
    formData.append("premium", premium.value);
    formData.append("featured", featured.value);
  }
  formData.append("youtube", youtube.value);

  const images = document.getElementById('image');
  const videos = document.getElementById('video');
  const imgCount = images.files.length;
  const vdoCount = videos.files.length;
  attachementList = [];
  attachCounter = 0;
  for (let i = 0; i < imgCount; i++) {
    attachementList.push({type: 1, file: images.files[i]})
  }
  for (let i = 0; i < vdoCount; i++) {
    attachementList.push({type: 2, file: videos.files[i]})
  }

  formData.append("image_count", imgCount);
  formData.append("video_count", vdoCount);

  fileUploadProgress.style.display = "flex";
  fileUploadProgress.querySelector('#progress').innerHTML= '<i class="fas fa-spinner fa-spin"></i> Loading...';
  fileUploadProgress.querySelector('#fileCounter').innerHTML= '';
  const result = await postFormToServer(``, formData);
  if (result.status) {
    if(result.data.post_url) postUrl = result.data.post_url;
    uploadFileToServer(result.data.id);
  } else {
    alertify.error(result.msg);
  }
};

const finishFileUpload = () => {
  attachementList = [];
  attachCounter = 0;
  fileUploadProgress.style.display = "none";
  fileUploadProgress.querySelector('#progress').innerHTML= '';
  fileUploadProgress.querySelector('#fileCounter').innerHTML= '';
  hideBtnLoading(document.getElementById('submit-btn'));
  window.location.href = params.next ? params.next : postUrl;
}

const uploadFileToServer = async(post_id) => {
  if(attachCounter >= attachementList.length) return finishFileUpload();
  const attachRow = attachementList[attachCounter];
  attachCounter ++;

  fileUploadProgress.querySelector('#progress').innerHTML= '<i class="fas fa-spinner fa-spin"></i> Loading...';
  fileUploadProgress.querySelector('#fileCounter').innerHTML= `${attachCounter}/${attachementList.length}`;
  const result = await postToServer(`/post/create-attachement`, {
    "post_id": post_id, "post_type": attachRow.type, "file_name": attachRow.file.name, "file_type": attachRow.file.type
  });

  if (result.status) {
    const progressHandler = (event) => {
      // console.log(event);
      const percent = (event.loaded / event.total) * 100;
      fileUploadProgress.querySelector('#progress').innerHTML= `${attachRow.file.name} - <b>${Math.round(percent)}%</b> Completed`;
    }
    // fileUploadProgress.querySelector('#progress').innerHTML= '';
    
    const completeHandler = (event) => {
      // const res = JSON.parse(event.currentTarget.response);
      const resSatus = event.currentTarget.status;
      if(resSatus == 200 || resSatus == 201 || resSatus == 204) {
        // alertify.success("Uploaded successfully.");
        uploadFileToServer(post_id);
      } else {
        fileUploadProgress.style.display = "none";
        alertify.error("Something went wrong.");
      }
    }
    const errorHandler = (event) => {
      fileUploadProgress.style.display = "none";
      alertify.error("Something went wrong.");
      console.log(event);
    }
    const abortHandler = (event) => {
      fileUploadProgress.style.display = "none";
      alertify.error("Something went wrong.");
      console.log(event);
    }

    const formData = new FormData()
    for(key in result.data.aws_data.fields){
      formData.append(key, result.data.aws_data.fields[key]);
    }
    formData.append("file", attachRow.file);
    uploadFileForm(result.data.aws_data.url, formData, progressHandler, completeHandler, errorHandler, abortHandler);
    // alertify.success(result.msg);
  } else {
    fileUploadProgress.style.display = "none";
    alertify.error(result.msg);
  }
}