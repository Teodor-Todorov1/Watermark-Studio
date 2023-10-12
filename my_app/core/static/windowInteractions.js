// show static elements on scroll

let scroll =
  window.requestAnimationFrame ||
  function (callback) {
    window.setTimeout(callback, 1000 / 60);
  };

let elementsToShow = document.querySelectorAll(".show-on-scroll");

function loop() {
  elementsToShow.forEach(function (element) {
    if (isElementInViewport(element)) {
      element.classList.add("is-visible");
    } else {
      element.classList.remove("is-visible");
    }
  });

  scroll(loop);
}

loop();

function isElementInViewport(el) {
  let rect = el.getBoundingClientRect();
  return (
    (rect.top <= 0 && rect.bottom >= 0) ||
    (rect.bottom >=
      (window.innerHeight || document.documentElement.clientHeight) &&
      rect.top <=
        (window.innerHeight || document.documentElement.clientHeight)) ||
    (rect.top >= 0 &&
      rect.bottom <=
        (window.innerHeight || document.documentElement.clientHeight))
  );
}

// Go to top button
let topBTN = document.getElementById("toTopBTN");

window.onscroll = function () {
  scrollFunction();
};

function scrollFunction() {
  if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
    topBTN.classList.add("scrolled");
    topBTN.classList.remove("fadeOut");
  } else {
    topBTN.classList.remove("scrolled");
    topBTN.classList.add("fadeOut");
  }
}

let createBTN = document.getElementById("dropdown__face");
let items = document.getElementById("dropdown__items");

createBTN.onclick = function () {
  if (items.style.opacity === "1") {
    items.style.visibility = "hidden";
    items.style.opacity = "0";
    items.style.top = "50%";
  } else {
    items.style.visibility = "visible";
    items.style.opacity = "1";
    items.style.top = "calc(100% + 25px)";
  }
};
