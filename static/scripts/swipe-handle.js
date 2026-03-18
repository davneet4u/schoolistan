const handleHzSwipe = (element, leftHandler=()=>{}, rightHandler=()=>{}) => {
  let xDown = null;
  let yDown = null;

  element.addEventListener("touchstart", (evt) => {
    const firstTouch = getTouches(evt)[0];
    xDown = firstTouch.clientX;
    yDown = firstTouch.clientY;
  }, false );

  element.addEventListener("touchmove", (evt) => {
    if (!xDown || !yDown) {
        return;
    }

    var xUp = evt.touches[0].clientX;
    var yUp = evt.touches[0].clientY;

    var xDiff = xDown - xUp;
    var yDiff = yDown - yUp;

    if (Math.abs(xDiff) > Math.abs(yDiff)) {
      /*most significant*/
      if (xDiff > 0) {
        /* right swipe */
        rightHandler();
      } else {
        /* left swipe */
        leftHandler();
      }
    } else {
      if (yDiff > 0) {
        /* down swipe */
        console.log("down swipe");
      } else {
        /* up swipe */
        console.log("up swipe");
      }
    }
    /* reset values */
    xDown = null;
    yDown = null;

  }, false);
};

getTouches = (evt) => {
  return evt.touches || evt.originalEvent.touches;
};
