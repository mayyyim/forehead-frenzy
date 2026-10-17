# Handoff — 2026-10-17 — Pages 部署 + 三个连环 bug 修复

接手人第一步：读 `logs/TODO.md` 的「进行中」。本 packet 记的是**三个 bug 的因果链**
和**本会话最该吸取的方法论教训**，比单独看 commit 更容易理解为什么代码长这样。

线上：https://mayyyim.github.io/forehead-frenzy/ （权威，tilt 只在这里能用）
备用：https://claude.ai/artifact/XxgLQ8fHpYnQF1gVUYMfYA （Version 6，iframe 内，tilt 不保证）

## 一条源码，两个宿主（改代码前必读）

- `index.html` = **完整独立文档**（有 doctype/charset/viewport/reset），Pages 原样托管
- `artifact.html` = 由 `python3 build.py` 从 index.html **自动生成**的片段（剥掉文档外壳），
  因为 claude.ai artifact 运行时会自己套 doctype/head/body，带外壳的文件它不收

**永远不要手改 artifact.html**，改完 index.html 跑一次 `build.py`。
两个宿主都要推：`git push` 管 Pages，artifact 要用 Artifact 工具重新 publish 到同一 URL。

## 三个 bug 的因果链（都已修，别改回去）

### Bug 1：输入在第一个词之后全哑
`resolve()` 清掉防连击标志 `armed`，但**复位它的代码只存在于传感器回调里**。
传感器静默（iframe 内 / 权限被拒）→ `armed` 永远停在 false → 点击区每局只能得分一次。
修法：复位收敛成唯一的 `rearm()`，由 **100ms 回合时钟**驱动，不依赖任何传感器流量。

### Bug 2：点 Start 毫无反应（第一层）
`begin()` 连着请求 `DeviceMotionEvent` 和 `DeviceOrientationEvent` 两个权限。
**iOS 一个用户手势只允许一次权限请求，第二次同步抛 `NotAllowedError`**，
而代码只挂了 `.catch()`（管 promise 拒绝，管不了同步抛）→ 异常打断 `begin()`。
修法：①只请求一个权限门（iOS 上 motion 权限覆盖 orientation）②try/catch 包同步抛
③**`begin()` 先开局，音效/权限/全屏/常亮全部挪到开局之后并各自隔离** —— 它们都不是
玩游戏的必要条件，所以都不该有能力阻止开局。第③条是结构修正，比前两条重要。

### Bug 3：点 Start 毫无反应（真正的根因）＋ `round.endAt` 报错
`index.html` 当时还是**为 artifact 环境写的片段**，被我原样搬到 Pages。
artifact 运行时会在外面套一层 head，里面有两样东西代码**隐式依赖**了：
- `[hidden]{display:none !important}` —— `.screen{display:flex}` 是**作者样式**，
  会压过 `hidden` 属性的 UA 默认 `display:none`。没有这条 !important 规则
  → **四个界面同时渲染**，堆成一长页 → 点 Start 确实切了 hidden 标志，但视觉上毫无变化。
- viewport meta —— 手机按桌面宽度渲染。

而「界面全部可见」又直接导致了用户看到的 `null is not an object (evaluating 'round.endAt')`：
游戏界面的退出按钮和点击区在设置界面上就是可点的 → 点到就 `finish()` 把 `round` 置 null
→ 倒计时里那个还在排队的 `setTimeout(live, 650)` 随后触发 → `live()` 里 `round.endAt` 炸。
修法：补文档外壳 + `live()`/`tickClock()` 开头 `if(!round) return` + `finish()` 取消倒计时 interval。

## 方法论教训（本会话最值钱的部分）

1. **降级路径不能把状态机挂在主路径的事件流上**（Bug 1）。
2. **可选的副作用不能前置于核心动作**（Bug 2）。音效、权限、全屏、常亮都是"有更好"，
   把它们放在 `show("count")` 之前，等于让四个环境依赖各自持有一张否决票。
3. **换宿主时，先问「原宿主偷偷给了我什么」**（Bug 3）。这是本会话最大的失误：
   artifact 运行时注入的 reset 和 meta 是隐式契约，搬到裸托管就全没了。
4. **远程设备上的「不管用」要靠自证，不要靠猜**。前三轮全靠猜，三轮全错。
   真正提速的是两件事：①页面里加 `#oops` 错误条 + `#diag` 传感器诊断行，
   让用户直接念出错误信息 ②`/tmp/h2.js` 那个**虚拟时钟 DOM stub**，
   在 node 里无头跑完整局（含「倒计时途中退出再重开」），不用等用户手机。
   **建议：以后改游戏逻辑先跑它。** 它能抓的：同步抛异常、缺失 id、状态机死锁、计分错误。
   它抓不到的：CSS/布局、真机传感器行为 —— 所以 Bug 3 它没抓住（纯 CSS 层）。
5. **加 build stamp**。Pages 带 `cache-control: max-age=600`，旧缓存和真 bug 症状完全一样。
   设置页底部现在印 `build 6 · 2026-10-17`，先对版本号再谈 bug。

## PENDING

- **唯一真待办**：用户在 `?v=6` 上实测。先让其确认底部印的是 `build 6`，否则还在吃缓存。
- 若 tilt 仍不动 → 念设置页那行 `#diag` 诊断读数，对照 `TODO.md` 的分支表定位。
- 低优先级功能：多选主题自由组合 / 词库分 easy-hard / 漏词进下一局重练。

## RISKS

1. **缓存**。Pages 的 `max-age=600` 没法配。换版本后让用户带 `?v=N` 打开，或等 10 分钟。
2. **自动符号校准有前置条件**：需要用户在设置页把手机拿在 `|beta|<60 且 |gamma|<60`，
   且 devicemotion 与 deviceorientation 两个事件都有数据。只给一个则校准不触发，
   退回按 UA 猜（iOS = -1）。不致命，有 `Flip up/down` 兜底。
3. **仓库是 public**（免费版 Pages 硬要求）。目前只有游戏页面和文档，无凭证。
   以后别往这个仓库放私密内容。
4. **两个宿主可能漂移**。只推一边会导致行为不一致；`build.py` 只保证内容一致，不保证推送。

## NEXT

1. 拿用户实测结果 → 关掉 TODO「进行中」，或按 `#diag` 读数走分支表。
2. tilt 确认可用后：问词库难度和回合时长合不合适 —— 这是唯一需要真人反馈才能调的参数。
3. 要加功能优先「漏掉的词进下一局重练」：`round.log` 已存 `{w, got}`，数据结构不用动。
