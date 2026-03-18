// --------------- user category selection ---------------
const loadSelectedCats = async () => {
  const result = await getFromServer(`/account/user-categories`);
  if (result.status) {
    const userCatList = document.getElementById("user-cat-list");
    const parentCats = result.data.parent_categories;
    const subCats = result.data.sub_categories;
    const userCatIds = result.data.user_categories;
    userCatList.innerHTML = "";
    let html = "";
    userCatList.insertAdjacentHTML("beforeend", `<div class="full" id="u_cat_box_0"></div>`);
    parentCats.forEach((parentCat) => {
      html = `
        <p class="cat-g-title">${parentCat[1]}</p>
        <div style="margin-left: 20px;" id="u_cat_box_${parentCat[0]}"></div>
      `;
      userCatList.insertAdjacentHTML("beforeend", html);
    });
    let target = null;
    html = "";
    // console.log(userCatIds);
    subCats.forEach((subCat) => {
      target = document.getElementById(`u_cat_box_${subCat[2]}`);
      if (!target) target = document.getElementById("u_cat_box_0");
        html = `
          <p class="check full">
            <input type="checkbox" id="u_cat_${subCat[0]}" value="${subCat[0]}" ${userCatIds.includes(subCat[0]) && 'checked'}>
            <label for="u_cat_${subCat[0]}">${subCat[1]}</label>
          </p>
        `;
        target.insertAdjacentHTML("beforeend", html);
      // console.log(subCat);
    });
    showFlexPopup('select-topics');
  } else alertify.error(result.msg);
};
const saveUserCategories = async (btn) => {
  showBtnLoading(btn);
  const userCats = document.querySelectorAll("#user-cat-list input[type=checkbox]:checked");
  const userCatArr = [];
  userCats.forEach(userCat => {
    userCatArr.push(parseInt(userCat.value));
  });
  const result = await postToServer(`/account/user-categories`, {
    user_categories: userCatArr.toString()
  });
  if (result.status) {
    alertify.success(result.msg);
    window.location.reload();
  } else alertify.error(result.msg);
  hideBtnLoading(btn);
  hideFlexPopup('select-topics');
}
// --------------- --------------- ---------------
