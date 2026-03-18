//
var cropper = null;
const initiateCropperTool = (
  imgInpObj = null,
  callback = () => {},
  aspectRatio = 1 / 1,
  dimension = { width: 250, height: 250 },
) => {
  let cropperPopup = document.getElementById("cropperPopup");
  if (cropperPopup) cropperPopup.remove();
  if (imgInpObj && imgInpObj.files && imgInpObj.files.length > 0) {

    const popupHtml = `
      <div class="popup" id="cropperPopup">
        <div class="overlay"></div>
        <div class="content">
          <div id="cropperResult"></div>
          <div style="text-align: end; margin-top: 20px;">
            <button class="btn secondary" id="cropperBtnCancel">Cancel</button>
            <span>&nbsp;</span>
            <button class="btn primary" id="cropperBtnCrop">Crop</button>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML("beforeend", popupHtml);

    cropperPopup = document.getElementById("cropperPopup");
    document.getElementById("cropperBtnCancel").addEventListener("click", () => getCroppedPicture(dimension, callback, false));
    document.getElementById("cropperBtnCrop").addEventListener("click", () => getCroppedPicture(dimension, callback, true));

    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target.result) {
        const result = document.getElementById("cropperResult");
        const img = document.createElement("img");
        img.id = "image";
        img.src = e.target.result;
        // clean result before
        result.innerHTML = "";
        // append new image
        result.appendChild(img);
        img.style.maxWidth = "100%";
        img.style.display = "block";
        cropperPopup.style.display = "flex";
        cropper = new Cropper(img, { aspectRatio: aspectRatio });
        console.log(cropper);
      }
    };
    reader.readAsDataURL(imgInpObj.files[0]);
  } else {
    callback(null);
  }
};
const getCroppedPicture = async (dimension, callback, status) => {
  let imgSrc = null;
  if (status) {
    imgSrc = cropper.getCroppedCanvas(dimension).toDataURL();
  }
  cropper = null;
  document.getElementById("cropperPopup").remove();
  callback(imgSrc);
};
