/* Regression test for the two tilt-input bugs reported on 2026-11-15:
     A. one skip gesture consumed TWO words
     B. shaking the phone during the 3-2-1 countdown already scored words
   Run against another build to prove the test is not vacuous:
     node tools-headless-tilt-test.js /path/to/old/index.html
*/
const file = process.argv[2] || undefined;
const R = require(__dirname + "/tools-vdom.js")({
  perm: "granted", file,
  store: {"ff.v1.mode":'"tilt"', "ff.v1.secs":"60", "ff.v1.sign":"1", "ff.v1.calibrated":"true"}
});

const G = 9.8, STEP = 20;
/* The page gets the raw accelerometer triple and does its own normalising, so the test
   must hand it physical values -- including the lateral acceleration of a real swing. */
function at(z, x){
  x = x || 0;
  R.motion(x, -Math.sqrt(Math.max(0, G*G - z*z)), z);
}
function hold(ms, z, x){ for(let t = 0; t < ms; t += STEP){ at(z, x); R.advance(STEP); } }
function shake(ms, amp){                       /* a wobble that sweeps through upright */
  for(let t = 0; t < ms; t += STEP){ at(amp * Math.sin(2*Math.PI*t/400)); R.advance(STEP); }
}
const got = () => Number(R.text("tGood")), passed = () => Number(R.text("tBad"));

let fails = 0;
function check(label, actual, expected){
  const ok = actual === expected;
  if(!ok) fails++;
  console.log((ok ? "  PASS  " : "  FAIL  ") + label + " -> " + actual + " (expected " + expected + ")");
}

(async function(){
  R.pool.enableBtn.click();                    /* "Enable tilt" on the setup screen */
  await R.flush();
  console.log("sensor attached:", R.sensorAttached());
  hold(400, 0);                                /* held still: calibrates the gravity scale */

  console.log("\nB. shaking the phone during the countdown");
  R.pool.startBtn.click();
  shake(1600, 9.3);                            /* violent wobble while 3-2-1 runs */
  R.advance(2000);                             /* countdown ends, round goes live */
  check("screen-play visible", R.pool["screen-play"].hidden, false);
  check("words scored during countdown", got() + passed(), 0);

  console.log("\nA. one pass gesture must consume exactly one word");
  hold(400, 0);                                /* phone settles on the forehead */
  const w1 = R.text("word");
  for(let i = 1; i <= 7; i++){ at(9.3 * i/7); R.advance(STEP); }   /* swing up: pass */
  hold(260, 9.3, 30);                          /* mid-swing: lateral accel fakes upright */
  for(let i = 7; i >= 1; i--){ at(9.3 * i/7); R.advance(STEP); }   /* swing back down */
  hold(200, 0);
  check("passed after one up-gesture", passed(), 1);
  check("got after one up-gesture", got(), 0);
  check("word advanced", R.text("word") !== w1, true);

  console.log("\nC. input comes back, and a down-gesture still scores");
  hold(900, 0);                                /* settle -> rearm */
  for(let i = 1; i <= 7; i++){ at(-9.3 * i/7); R.advance(STEP); }  /* swing down: got it */
  hold(260, -9.3, 30);
  for(let i = 7; i >= 1; i--){ at(-9.3 * i/7); R.advance(STEP); }
  hold(200, 0);
  check("got after one down-gesture", got(), 1);
  check("passed still", passed(), 1);

  console.log("\nE. a quick flick of the wrist still registers");
  hold(900, 0);
  const before = passed();
  for(let i = 1; i <= 3; i++){ at(9.3 * i/3, 15); R.advance(STEP); }   /* fast swing up */
  at(9.3); R.advance(STEP); at(9.3); R.advance(STEP);                  /* still at the top */
  for(let i = 2; i >= 0; i--){ at(9.3 * i/3, -15); R.advance(STEP); }  /* straight back */
  hold(200, 0);
  check("the flick scored a pass", passed() - before, 1);

  console.log("\nD. quitting mid-round, then the recap");
  R.key("Escape");
  check("screen-done visible", R.pool["screen-done"].hidden, false);
  check("final score", R.text("doneScore"), "1");
  check("error banner", R.pool.oops.hidden, true);
  R.advance(5000);
  check("error banner after the dust settles", R.pool.oops.hidden, true);

  console.log(fails ? "\n" + fails + " CHECK(S) FAILED" : "\nall checks passed");
  R.restore();
  process.exit(fails ? 1 : 0);
})();
