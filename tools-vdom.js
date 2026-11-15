/* Virtual-clock + stub-DOM rig, shared by the headless tests.
   There is deliberately ONE copy of this: the tap test and the tilt test have to agree
   about what the environment is, or a fix proved in one can be broken by the other. */
const fs = require("fs");

module.exports = function rig(opt){
  opt = opt || {};                      /* {perm:"granted"|"throw", store:{}, file} */
  const html = fs.readFileSync(opt.file || (__dirname + "/index.html"), "utf8");
  const js = html.split("<script>")[1].split("</script>")[0];
  const ids = new Set([...html.matchAll(/id="([^"]+)"/g)].map(m => m[1]));
  /* Which elements start out hidden has to come from the markup. A rig that reports every
     element as visible turns "is the error banner up?" and "did the screen switch?" into
     assertions that cannot fail. */
  const hiddenAtRest = new Set();
  for(const tag of html.match(/<[a-zA-Z][^>]*>/g) || []){
    const id = /\sid="([^"]+)"/.exec(tag);
    if(id && /\shidden(?=[\s=>/])/.test(tag)) hiddenAtRest.add(id[1]);
  }

  let vclock = 1000, q = [], seq = 0;
  const realNow = Date.now;
  Date.now = () => vclock;
  global.setTimeout  = (fn, ms) => { const h = {id:++seq, at:vclock+(ms||0), fn, rep:0};     q.push(h); return h.id; };
  global.setInterval = (fn, ms) => { const h = {id:++seq, at:vclock+(ms||0), fn, rep:ms||1}; q.push(h); return h.id; };
  global.clearInterval = id => { q = q.filter(h => h.id !== id); };
  global.clearTimeout = global.clearInterval;

  function advance(ms){
    const end = vclock + ms;
    for(let guard = 0; guard < 200000; guard++){
      const next = q.filter(h => h.at <= end).sort((a,b) => a.at - b.at)[0];
      if(!next) break;
      vclock = next.at;
      if(next.rep){ next.at = vclock + next.rep; } else { q = q.filter(h => h !== next); }
      try{ next.fn(); }catch(e){ console.log("TIMER THREW:", e.message); }
    }
    vclock = end;
  }

  const pool = {};
  function mkEl(id){ return {
    id, _text:"", className:"", hidden: hiddenAtRest.has(id), innerHTML:"", dataset:{}, style:{}, listeners:{}, children:[],
    get textContent(){ return this._text; }, set textContent(v){ this._text = String(v); },
    addEventListener(t, f){ const l = this.listeners[t] = this.listeners[t] || []; if(l.indexOf(f) < 0) l.push(f); },
    setAttribute(){}, getAttribute(){ return null; },
    classList:{ toggle(){}, add(){}, remove(){} }, querySelectorAll(){ return []; },
    click(){ (this.listeners.click || []).forEach(f => f({stopPropagation(){}, preventDefault(){}})); }
  };}

  const docL = {};
  global.document = {
    getElementById: id => pool[id] || (pool[id] = ids.has(id) ? mkEl(id) : null),
    addEventListener(t, f){ const l = docL[t] = docL[t] || []; if(l.indexOf(f) < 0) l.push(f); },
    documentElement:{}, querySelectorAll(){ return []; }
  };

  const winL = {};
  function DME(){}
  DME.requestPermission = opt.perm === "granted"
    ? () => Promise.resolve("granted")
    : () => { throw Object.assign(new Error("one per gesture"), {name:"NotAllowedError"}); };

  const store = Object.assign({}, opt.store || {});
  global.window = {
    DeviceMotionEvent: DME, DeviceOrientationEvent: undefined,
    AudioContext: undefined, webkitAudioContext: undefined,
    addEventListener(t, f){ const l = winL[t] = winL[t] || []; if(l.indexOf(f) < 0) l.push(f); },
    scrollTo(){}, self:1, top:1,
    localStorage:{ getItem: k => (k in store ? store[k] : null), setItem:(k,v) => store[k] = v }
  };
  global.localStorage = window.localStorage;
  global.navigator = { userAgent:"iPhone", vibrate(){}, wakeLock:undefined };

  eval(js);

  /* The game only subscribes to the sensor after the permission promise resolves, and
     that resolution is a microtask -- so a caller must flush it before sending samples. */
  const flush = () => new Promise(r => setImmediate(r));   /* runs after the microtask queue */

  return {
    pool, advance, flush, store,
    text: id => (pool[id] ? pool[id].textContent : "(none)"),
    sensorAttached: () => !!(winL.devicemotion && winL.devicemotion.length),
    /* Raw accelerometer triple, exactly as the page receives it: the normalisation and
       the shake test both live in the page, so the test must not pre-digest the values. */
    motion(x, y, z){
      (winL.devicemotion || []).forEach(f => f({accelerationIncludingGravity:{x, y, z}}));
    },
    key(k){ (docL.keydown || []).forEach(f => f({key:k, preventDefault(){}})); },
    restore(){ Date.now = realNow; }
  };
};
