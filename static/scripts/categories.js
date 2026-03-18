const multiple = document.currentScript.getAttribute('multiple') == 1 ? true : false;
const categories = document.getElementById("categories");
const categoriesHolder = document.getElementById("categories-holder");
const loadCategories = async (catId = null, catObj = null) => {
  let parentQ = "";
  let catBox = null;
  if (catId) {
    parentQ = `?parent_id=${catId}`;
    catBox = document.getElementById(`cat_${catId}_subcats`);
  } else {
    catBox = document.getElementById("all-cats");
  }
  catBox.innerHTML = "";
  if (catObj) {
    catObj.parentNode.insertAdjacentHTML(
      "beforeend",
      `<i id="load-${catId}" class="fa-solid fa-spinner fa-spin"></i>`
    );
  }
  const result = await getFromServer(`/post/category-list${parentQ}`);
  if (catObj) {
    document.getElementById(`load-${catId}`).remove();
  }
  if (result.status) {
    result.data.forEach((row) => {
      const html = `
          <p class="check full">
            <input type="checkbox" id="cat_${row[0]}" data-title="${row[1]}" value="${row[0]}" onchange="changeCategories(this);">
            <label id="cat_l_${row[0]}" for="cat_${row[0]}">${row[1]}</label>
          </p>
          <div style="margin-left: 20px;" id="cat_${row[0]}_subcats" data-parent-id="${row[0]}"></div>
        `;
      catBox.insertAdjacentHTML("beforeend", html);
    });
    catBox.insertAdjacentHTML(
      "beforeend",
      `<p class="full"><a onclick="addNewCatForm(this)" href="javascript:void(0);"><i class="fa-solid fa-plus"></i> Add new</a></p>`
    );
  }
};
const changeCategories = async (newCat) => {
  multiple ? await changeCatMultiple(newCat) : await changeCatSingle (newCat);
};
const changeCatMultiple = async (newCat) => {
  if (newCat.checked) {
    if(document.getElementById(`cat_${newCat.value}_subcats`).innerHTML == "") {
      await loadCategories(newCat.value, newCat);
    }
    const parentCatInput = document.getElementById(`cat_${newCat.parentNode.parentNode.getAttribute('data-parent-id')}`);
    if(parentCatInput) parentCatInput.checked = false;
  }
  const catInputs = document.querySelectorAll("#all-cats input[type=checkbox]:checked");
  const catIdsArr = [];
  let selectedCatsHtml = "";
  catInputs.forEach(catInput => {
    catIdsArr.push(parseInt(catInput.value));
    selectedCatsHtml += `<span>${catInput.getAttribute('data-title')}</span>`;
  });
  document.getElementById('categories-holder').innerHTML = selectedCatsHtml;
  document.getElementById('categories').value = catIdsArr.toString();
}
const changeCatSingle = async (newCat) => {
  if (categories.value != "") {
    document.getElementById(`cat_${categories.value}`).checked = false;
  }
  if (newCat.checked) {
    categories.value = newCat.value;
    categoriesHolder.innerHTML = `<span>${newCat.getAttribute('data-title')}</span>`;
    if(document.getElementById(`cat_${newCat.value}_subcats`).innerHTML == "") {
      await loadCategories(newCat.value, newCat);
    }
  } else {
    categories.value = "";
    categoriesHolder.innerHTML = "Select a category";
  }
}
// add categories and sub categories
const createCategory = async (btn) => {
  const parentId = btn.parentNode.parentNode.getAttribute("data-parent-id");
  const catTitle = btn.parentNode.querySelector("input").value.trim();
  if (catTitle == "") {
    alert("Please enter category.");
    return;
  }
  showIconBtnLoading(btn);
  const result = await postToServer(`/post/category/create`, {
    category_title: catTitle,
    parent_id: parentId ? parentId : null,
  });
  hideIconBtnLoading(btn);
  if (result.status) {
    parentId ? loadCategories(parentId) : loadCategories();
    alertify.success(result.msg);
  } else {
    alertify.error(result.msg);
  }
};
const addNewCatForm = (obj) => {
  console.log(obj.parentNode.parentNode);
  const html = `
      <p class="row full" style="flex-direction: row;">
        <input type="text" />&nbsp;
        <button class="btn pri" onclick="createCategory(this)"><i class="fa-solid fa-floppy-disk"></i></button>
      </p>`;
  obj.parentNode.parentNode.insertAdjacentHTML("beforeend", html);
};
