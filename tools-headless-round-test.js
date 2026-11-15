/* Plays a whole round headlessly on the TAP path -- the degraded path, where the sensor
   permission is refused and no readings ever arrive. It has to keep working on its own:
   the input used to die after one word because re-arming hung off the sensor stream. */
const R = require(__dirname + "/tools-vdom.js")({ perm: "throw", file: process.argv[2] });

let fails = 0;
function check(label, actual, expected){
  const ok = actual === expected;
  if(!ok) fails++;
  console.log((ok ? "  PASS  " : "  FAIL  ") + label + " -> " + actual + " (expected " + expected + ")");
}

console.log("1. the round starts");
R.pool.startBtn.click();
check("screen-count visible", R.pool["screen-count"].hidden, false);
R.advance(4000);
check("screen-play visible", R.pool["screen-play"].hidden, false);
check("a word is on screen", R.text("word").length > 0, true);
check("tap hint (no sensor)", R.text("hintDown"), "▼ Tap down here — got it");
check("no error banner", R.pool.oops.hidden, true);

console.log("\n2. six taps, every third one a pass");
const words = [];
for(let i = 1; i <= 6; i++){
  words.push(R.text("word"));
  (i % 3 === 0 ? R.pool.zoneTop : R.pool.zoneBot).click();
  R.advance(800);
}
check("got", R.text("tGood"), "4");
check("passed", R.text("tBad"), "2");
check("distinct words served", new Set(words).size, 6);

/* GATE_MS is 170ms on purpose: a longer dead window swallowed roughly every fifth fast
   tap. Tightening the tilt path must not quietly slow the tap path back down. */
console.log("\n3. two taps 200ms apart both register");
R.pool.zoneBot.click();
R.advance(200);
R.pool.zoneBot.click();
R.advance(400);
check("got after the fast pair", R.text("tGood"), "6");

console.log("\n4. the clock runs out");
R.advance(60000);
check("screen-done visible", R.pool["screen-done"].hidden, false);
check("score", R.text("doneScore"), "6");
check("split", R.text("doneSplit"), "6 got · 2 passed");
check("no error banner", R.pool.oops.hidden, true);

console.log(fails ? "\n" + fails + " CHECK(S) FAILED" : "\nall checks passed");
R.restore();
process.exit(fails ? 1 : 0);
