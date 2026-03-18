// --------------- side navigation hide and show ---------------
document.getElementById("menu").onclick = () => {
  document.getElementsByClassName("side-nav")[0].style.left = "0";
};
document.getElementById("close").onclick = () => {
  document.getElementsByClassName("side-nav")[0].style.left = "-250px";
};
// --------------- side navigation drow down handling ---------------
const btns = document.querySelectorAll(".side-nav a.d-btn");
const boxes = document.querySelectorAll(".side-nav .d-box");
var expandedId = "";
const collapseAll = () => {
  btns.forEach((btn) => {
    document.querySelector("a#" + btn.id + " i:last-child").className =
      "fa-solid fa-caret-down";
  });
  boxes.forEach((box) => (box.style.maxHeight = "0"));
};
const expand = (id) => {
  collapseAll();
  const box = document.querySelector(".side-nav #" + id + "-box");
  if (id === expandedId) {
    expandedId = "";
    document.querySelector("a#" + id + " i:last-child").className =
      "fa-solid fa-caret-down";
    box.style.maxHeight = "0";
  } else {
    expandedId = id;
    document.querySelector("a#" + id + " i:last-child").className =
      "fa-solid fa-caret-right";
    box.style.maxHeight = box.children.length * 55 + "px";
  }
};
btns.forEach((btn) => (btn.onclick = () => expand(btn.id)));
const path = window.location.pathname;
if (path.includes("/teacher") || path.includes("/user")) {
  expand("drop-1");
} else if (path.includes("/categor") || path.includes("/sub-categor")) {
  expand("drop-2");
} else {
  collapseAll();
}