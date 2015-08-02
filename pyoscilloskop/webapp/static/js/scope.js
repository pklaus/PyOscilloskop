var wd, ht;

/* For Frame rate */
var lastTime;
var frames        = 0;
var totalTime     = 0;
var updateTime    = 0;
var updateFrames  = 0;

function printf(text) {
    document.writeln(text);
}

function getRandom(scale) {
    return (Math.random() * scale);
}

function getNegate(scale) {
  if (0 == ((Math.floor(Math.random() * scale))/7)) {
    return -1;
  } else {
    return 1;
  }
}           

function initiateFPS() {
  /* For Frame rate - store initial time */
  lastTime = (new Date()).getTime();
}

function updateFPS() {
  /* update Frame rate */
  var now      = (new Date()).getTime();

  var delta    = now - lastTime;
  lastTime     = now;
  totalTime    = totalTime + delta;
  updateTime   = updateTime + delta;

  frames       = frames + 1;
  updateFrames = updateFrames + 1;

  if (1000 < updateTime) {
    document.getElementById('fps').innerHTML = "FPS AVG: " + Math.floor(1000*frames/totalTime) + " CUR: " + Math.floor(1000*updateFrames/updateTime);
    updateTime   = 0;
    updateFrames = 0;
  }
}

function colorToHex (r,g,b) {
  var rgb = b | (g << 8) | (r << 16);
  if (0 == r) {
      var rPad = '00';
      if (0 == g) {
          var gPad = '00';
          if (0 == b) {
              var bPad = '00';
              return '#' + rPad + gPad + +bPad;
              }
          else {
              return '#' + rPad + gPad + rgb.toString(16);
              }
          }
      else {
          return '#' + rPad + rgb.toString(16);
          }
      }
  return '#' + rgb.toString(16);
}

function drawCanvas () {
  printf('<canvas id="canvas" width="'+wd+'" height="'+ht+'"></canvas>');
  printf('<font color = "white"><b id="fps"></b></font>');
  }

function alterCanvas() {
  var canvas = document.getElementById("canvas");

  /* Movement of the XY line stroke */
  var moveX   = 0;
  var moveY   = 0;
  /* Number of locations to draw on */
  var n       = 1000;
  /* Number of iterator dots from the above */
  var mainCtr = 1/n;
  /* Counter to move froward across the screen */
  var ctr     = 0;

  function reset() {
    // clear canvas
    ctx.clearRect(0,0,wd,ht);
  }
  
  function redraw() {
    updateFPS();
    reset();
    ctx.strokeStyle = colorToHex(getRandom(50),getRandom(50),getRandom(50));
    ctx.fillStyle   = colorToHex(getRandom(200),getRandom(200),getRandom(200));
  
    /*
      Now we are going to project an oscilloscope with 'n' section points
      Middle of the screen Y location i.e. is where this is set as of now.
  
      The height can be adjusted later on. As of now
      the height location or Y axis is (ht / 2) + ( rand() * (+1 or -1) ).
  
      e.g. The width location or X axis are for 11 points
      wd  5wd  3wd  7wd  wd  9wd  5wd  11wd  3wd  13wd  7wd
      --  ---  ---  ---  --  ---  ---  ----  ---  ----  ---
      04  016  008  016  02  016  008  0016  004  0016  008
    */
  
    ctr = 0;
    ctx.beginPath();
  
    while (1 > ctr) {
      moveX  = wd * ctr;
      moveY  = ht/2 + (Math.floor(getRandom(100)) * getNegate(10));
      ctx.lineTo(moveX, moveY);
      ctr = ctr + mainCtr;
    }
  
    ctx.closePath();
    ctx.stroke();
    ctx.fill();
  }
  
  if (canvas.getContext) {
    var ctx = canvas.getContext("2d");
    ctx.globalAlpha = 1;
    ctx.lineWidth   = 1;
    initiateFPS();
    window.canvasTimer = setInterval(redraw, 0.01);
  } else {
    printf('<font color = "white"><b id="fps1">No HTML5</b></font>');
  }
}

function godsMain() {
  drawCanvas();
  alterCanvas();
}
