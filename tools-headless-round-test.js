// Virtual-clock harness: plays a whole round headlessly and checks scoring repeats.
const fs = require("fs");
const html = fs.readFileSync("/Users/may/projects/forehead-frenzy/index.html","utf8");
const js = html.split("<script>")[1].split("</script>")[0];
const ids = new Set([...html.matchAll(/id="([^"]+)"/g)].map(m=>m[1]));

let vclock = 1000, q = [], seq = 0;
const realNow = Date.now;
Date.now = () => vclock;
global.setTimeout  = (fn,ms) => { const h={id:++seq,at:vclock+(ms||0),fn,rep:0}; q.push(h); return h.id; };
global.setInterval = (fn,ms) => { const h={id:++seq,at:vclock+(ms||0),fn,rep:ms||1}; q.push(h); return h.id; };
global.clearInterval = id => { q = q.filter(h=>h.id!==id); };
global.clearTimeout  = global.clearInterval;
function advance(ms){
  const end = vclock + ms;
  for(let guard=0; guard<200000; guard++){
    const next = q.filter(h=>h.at<=end).sort((a,b)=>a.at-b.at)[0];
    if(!next) break;
    vclock = next.at;
    if(next.rep){ next.at = vclock + next.rep; } else { q = q.filter(h=>h!==next); }
    try{ next.fn(); }catch(e){ console.log("TIMER THREW:", e.message); }
  }
  vclock = end;
}

const pool = {};
function mkEl(id){ return {
  id,_text:"",className:"",hidden:false,innerHTML:"",dataset:{},style:{},listeners:{},children:[],
  get textContent(){return this._text}, set textContent(v){this._text=String(v)},
  addEventListener(t,f){(this.listeners[t]=this.listeners[t]||[]).push(f)},
  setAttribute(){},getAttribute(){return null},
  classList:{toggle(){},add(){},remove(){}}, querySelectorAll(){return []},
  click(){(this.listeners.click||[]).forEach(f=>f({stopPropagation(){},preventDefault(){}}))}
};}
global.document = {
  getElementById:id => pool[id] || (pool[id] = ids.has(id) ? mkEl(id) : null),
  addEventListener(){}, documentElement:{}, querySelectorAll(){return []}
};
function DME(){} DME.requestPermission = () => { throw Object.assign(new Error("one per gesture"),{name:"NotAllowedError"}); };
const store = {};
global.window = { DeviceMotionEvent:DME, DeviceOrientationEvent:undefined,
  AudioContext:undefined, webkitAudioContext:undefined,
  addEventListener(){}, scrollTo(){}, self:1, top:1,
  localStorage:{getItem:k=>store[k]??null,setItem:(k,v)=>store[k]=v} };
global.localStorage = window.localStorage;
global.navigator = { userAgent:"iPhone", vibrate(){}, wakeLock:undefined };

eval(js);

const g = id => pool[id] ? pool[id].textContent : "(none)";
console.log("1. start  ->", (pool.startBtn.click(), "clicked"), "| screen-count hidden:", pool["screen-count"].hidden);
advance(4000);
console.log("2. after countdown | screen-play hidden:", pool["screen-play"].hidden, "| word:", JSON.stringify(g("word")));
console.log("   hint:", JSON.stringify(g("hintDown")), "| error banner:", pool.oops.hidden ? "none" : g("oops"));

const words = [];
for(let i=1;i<=6;i++){
  words.push(g("word"));
  (i % 3 === 0 ? pool.zoneTop : pool.zoneBot).click();   // every 3rd one is a pass
  advance(800);
  console.log(`   tap ${i}: got=${g("tGood")} passed=${g("tBad")} nextWord=${JSON.stringify(g("word"))}`);
}
console.log("3. distinct words served:", new Set(words).size, "of", words.length);
advance(60000);
console.log("4. round ended | screen-done hidden:", pool["screen-done"].hidden,
            "| score:", g("doneScore"), "| split:", g("doneSplit"));
console.log("5. error banner at end:", pool.oops.hidden ? "none" : g("oops"));
Date.now = realNow;
process.exit(0);
