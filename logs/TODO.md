# TODO — Forehead Frenzy（英文你比划我猜）

**今晚用这个地址**：https://mayyyim.github.io/forehead-frenzy/ ← 顶层 HTTPS，传感器不被拦
备用（功能相同，但在 iframe 里，tilt 可能不工作）：https://claude.ai/artifact/XxgLQ8fHpYnQF1gVUYMfYA

源码：`index.html`（单文件，无依赖无构建）。改完 `git push` 即自动重新部署 Pages。
仓库：https://github.com/mayyyim/forehead-frenzy （public，Pages 免费版要求 public）

## 进行中
- [ ] **真机复测 build 16 的两个输入修复**（agent: 主 Claude，起始: 2026-11-15）
  下次打开第一步：让用户确认设置页底部印的是 `build 16`（否则还在吃 Pages 的 10 分钟缓存，
  带 `?v=16` 打开），然后只验两件事：
  - 一次 skip 动作只跳**一个**词（挥回额头途中不再误判第二次）
  - 3-2-1 倒计时期间随便晃手机，开局后比分必须是 0 / 0
  手感回归点：**快速甩腕**的 skip 仍要立刻响（这条是刻意保下来的取舍，见下方「已修 bug」第 2 条）。
  若手感变钝 → 调 `DWELL_MS`（150ms）；若仍偶发跳两个 → 调 `SHAKE`（0.30）或 `GATE_MS`（170ms）。

## 待办
- [ ] 继续打磨词库"好玩度"（用户已否掉 Body & feelings / 动物堆料 / Feelings & slang
      / 教科书式 Famous people / 中韩明星 / Scenes to mime）。优先级: 中
      判据：能不能当场比划出来，而不是"这个词算不算常用"
- [ ] 多选主题自由组合（现在单选 6 张卡之一）。优先级: 低
- [ ] 词库分 easy / hard 两档。优先级: 低
- [ ] 回合结束后把漏掉的词加入下一局重练。优先级: 低

## 已完成
- [x] **修复「一次 skip 跳两个词」+「倒计时晃手机就判定」**（完成: 2026-11-15，build 16）
      根因两条互相独立，见下方「已修 bug」。顺带把无头测试脚手架抽成 `tools-vdom.js`，
      新增 `tools-headless-tilt-test.js` 驱动传感器路径（旧版跑它 6 条 FAIL，新版全绿）。
- [x] **GitHub Pages 上 tilt 确认可用**（完成: 2026-11-15）
      用户已在真机上玩到能报告"skip 跳两个"，说明 tilt 路径本身通了，原「进行中」条目关闭。
- [x] **首页精简到 6 张卡 + 删掉 Scenes to mime**（完成: 2026-10-17，commit: d4d441d）
      12 张同质卡片选择成本太高 → 只留具名"好玩"牌组，其余 19 个源表归并成
      Everyday stuff(1439)；另加 Famous mix(716) 和 Mega mix(2135) 两张宽卡。
      配方只改分组、不动词表 → 覆盖率校验 2135/2135 零丢失。build 15。
- [x] 单文件网页游戏上线（完成: 2026-10-17）
      翻转检测 / 3-2-1 倒计时 / 30-60-90-120s / 计分 + 逐词回看 / 分 deck best score
      / Tap 降级模式 / 屏幕常亮 / 震动 + WebAudio / 方向键桌面操作
- [x] 词库 450 → 1672 词，10 → 23 主题 + 4 个混合 deck（完成: 2026-10-17）
- [x] 部署到 GitHub Pages 顶层 HTTPS 域名（完成: 2026-10-17，commit: 见 git log）
      动因：artifact 的 iframe 不放行传感器权限，tilt 在那里起不来
- [x] **修复「只有第一个词能点，第二个点不动」**（完成: 2026-10-17）
      根因见下方「已修 bug」段，和 tilt 失效是同一个根因的两个症状

## 阻塞中
- [!] 无阻塞。「进行中」等的是用户实测反馈，不是技术阻塞

---

## 已修 bug：输入在第一个词之后失效（务必别改回去）

`resolve()` 会把防连击标志 `armed` 置 false，但**复位它的代码只存在于
`devicemotion` / `deviceorientation` 回调里**。于是在传感器事件压根不来的设备上
（iframe 内 / 权限被拒），`armed` 永远停在 false —— 点击区每回合只能得分一次然后彻底哑掉。

这就是为什么「tilt 不管用」和「第二个词点不动」是**同一个根因**：
前者是传感器没数据，后者是「没数据」顺带把点击也锁死了。

修法：复位逻辑收敛成唯一一个 `rearm()`，由 **100ms 的回合时钟**驱动，不依赖任何传感器流量。
- tap 模式：闪屏结束即复位
- tilt 模式：仍要求手机回到接近竖直（`|tilt| < 0.34`）才接受下一次，防连击
- 传感器静默：直接按闪屏结束复位，点击照常可用

**教训**：降级路径（tap）绝不能把自己的状态机挂在主路径（传感器）的事件流上。

## 已修 bug（build 16）：一次 skip 跳两个词 / 倒计时晃手机就判定（务必别改回去）

两条症状看着像一件事，根因完全独立。

### 1. 倒计时期间输入全程带电
`begin()` 在 3-2-1 **之前**就建好了 `round`，而 `checkTilt()` 判活性的唯一依据是
`if(!round) return` —— 于是整个 3 秒倒计时里晃手机就在计分。无头测试里旧版吃掉 8 个词。

修法：新增**显式** `playing` 标志，只在 `live()` 到 `finish()` 之间为真；
`checkTilt` / `resolve` / 方向键全部改判 `playing`。`round` 不再兼任"输入是否生效"。
（`Escape` 退出仍在倒计时期间有效——退出不是判决。）

### 2. 挥回途中被一帧噪声骗着 re-arm
`rearm()` 只要**一帧** `|tilt| < 0.34` 就重新开火。而 `rawZ = a.z / m` 的 `m` 是
`accelerationIncludingGravity` 的模长，**含手臂自身的加速度**——快速挥动时 z 分量被稀释，
手机明明还歪着却读成接近竖直。于是 170ms 闸门一过就 re-arm，同一个挥动动作的后半段
又触发一次。旧版无头测试里一次挥动判出 6 pass + 4 got（过冲还会误判"猜对"）。

修法三件，缺一不可：
- `tilt` 改成一阶低通（`SMOOTH`=0.35）→ 单帧噪声不再是判决
- 用 `gBase`（模长的慢速 EMA）识别"正在晃"，`|m-gBase| > 0.30·gBase` 时标记
  `shakeUntil = now + 250ms`，**这段时间内不许 re-arm**
- re-arm 要求回到中性区并**连续稳住 150ms**（`DWELL_MS`），不是碰一下就算

**刻意没做的事**：`checkTilt()` 里**不**按 `shakeUntil` 拦判定。拦了会把**快速甩腕**整个吞掉——
甩动时横向加速度把倾角读数稀释，唯一读得准的就是挥到顶点那一两帧静止帧，而它们正好落在
屏蔽窗口里。重复触发要在**成因处**（`rearm`）治，不是在判定处。
`tools-headless-tilt-test.js` 的 §E 就是钉住这个取舍的测试：把那行加回去，§E 立刻 FAIL。

**教训**：`shakeUntil` 是**时间戳**而不是布尔量，传感器中途断流也会自动过期——
沿用的还是上次那条"降级路径不能把状态机挂在事件流上"。

## 关键设计决策（改代码前必读）

**翻转检测用重力在屏幕法线（device z 轴）上的投影，不是 beta/gamma 角度。**两个硬理由：
1. **绕 z 轴旋转不改变 z 分量**（数学恒等）→ 竖握横握斜握都一样，且全程不读
   `screen.orientation`，系统旋转锁开关不影响。
2. 贴额头是 `beta ≈ 90°`，**正好是 Z-X'-Y'' 欧拉角的万向锁死区**，角度判定会乱跳。

**iOS 与 Android 的 `accelerationIncludingGravity` 符号相反** → 自动校准：
趁手机在设置页被拿在手里（`|beta|<60 且 |gamma|<60`，远离死区）时，
用 `cos(beta)·cos(gamma)` 的符号交叉验证加速度计 z 的符号，结果存 `ff.v1.sign`。
兜底是界面上的 `Flip up/down`（存 `ff.v1.invert`）。

**阈值**：超过 0.60（离竖直约 37°）触发。回到 0.34 以内**且稳住 `DWELL_MS`=150ms** 才接受下一次
——"稳住"这个时间条件是 build 16 补的，光有角度条件会被挥回途中的一帧噪声骗过去（见「已修 bug」）。
另：喂给判定逻辑的 `tilt` 现在是 `SMOOTH`=0.35 的一阶低通，单帧噪声不再构成判决。

**必须 HTTPS 且必须顶层页面**：iOS 的 `DeviceMotionEvent.requestPermission()` 要求
secure context（所以 `file://` 和局域网 `http://` 都不行），而 iframe 还需要父页面带
`allow="accelerometer; gyroscope"`（所以 artifact 里不行）。GitHub Pages 两个条件都满足。
