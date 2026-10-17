# Handoff — 2026-10-17 — tilt 部署到顶层域名 + 输入锁死修复

接手人第一步：读 `logs/TODO.md` 的「进行中」，那里写了诊断读数怎么念。
本 packet 补充的是「这个 session 到底动了什么、删了什么、哪里还可能炸」。

## DONE

1. **游戏本体上线**（`index.html`，单文件，无依赖无构建步骤）
   - 23 个主题 + 4 个混合 deck，1672 个去重后的 A1–B1 英文词
   - 翻转检测 / 3-2-1 倒计时 / 30-60-90-120s / 计分 + 逐词回看 / 分 deck best score
   - Tap 降级模式 / 屏幕常亮 / 震动 + WebAudio 音效 / 桌面方向键操作

2. **部署到 GitHub Pages** → https://mayyyim.github.io/forehead-frenzy/
   - 仓库 https://github.com/mayyyim/forehead-frenzy ，**public**（免费版 Pages 的硬要求）
   - 动因：claude.ai artifact 把页面放在 iframe 里，不放行传感器权限，tilt 在那边起不来
   - artifact 版本仍维护在同一 URL（当前 Version 4），功能一致，但 tilt 不保证可用

3. **修复「第一个词之后输入全哑」** — 详细根因在 `logs/TODO.md` 的「已修 bug」段
   一句话版：防连击标志 `armed` 的复位代码只存在于传感器回调里，传感器静默时点击也被锁死。
   现收敛为单一 `rearm()`，由 100ms 回合时钟驱动。

4. **加了实时传感器诊断行**（设置页底部，等宽字）
   输出 `embedded / DeviceMotion / asks permission / permission / events / tilt`，
   目的是让「不管用」这种反馈直接变成可定位的事实，不用再靠猜。

## 本会话的删除操作（hook 关心的部分）

| 删了什么 | 为什么 | 影响哪里 |
|---|---|---|
| `if(cfg.mode === "tap") armed = true;`（`resolve()` 的 setTimeout 内） | 这是分模式的局部复位，只覆盖 tap 模式，是上面 3 号 bug 的病灶之一 | 已被 `rearm()` 完整取代并扩大覆盖面，**不要改回去** |
| `checkTilt()` 内的内联复位分支 | 同上，复位逻辑散落两处导致漏掉「传感器静默」这个 case | 已合并进 `rearm()` |
| `newdata.py` / `patch2-5.py` / `check.js` / `data.js` | 我自己生成的一次性词库注入和语法校验脚本，全在 session scratchpad 内 | 产物已全部落进 `index.html`，无保留价值；**未删除任何项目文件** |

**没有任何功能被删除**，所以不存在需要同步修正的过期文档描述。
`README.md` 和 `logs/TODO.md` 均已反映当前状态（含诊断行、Pages 部署、z 轴投影方案）。

## PENDING

- **唯一真待办**：用户在 Pages 地址上实测 tilt。等的是诊断行的内容，不是技术阻塞。
- 低优先级：多选主题自由组合 / 词库分 easy-hard 两档 / 漏掉的词进下一局重练。

## RISKS

1. **tilt 在 Pages 上仍失败的可能性**（低但非零）。排除顺序照 `TODO.md` 的诊断对照表走。
   若 `permission:granted` 且 `events` 在涨但方向不对 → 是符号自动校准没触发，点 `Flip up/down`。
2. **自动校准的触发条件有依赖**：需要用户在设置页把手机拿在 `|beta|<60 且 |gamma|<60` 的角度，
   且 `deviceorientation` 和 `devicemotion` 两个事件都有数据。若只给其中一个，
   校准不会发生，退回按 UA 猜的默认值（iOS = -1）。这不致命，有 Flip 按钮兜底。
3. **仓库是 public 的**。目前内容只有游戏页面和这些文档，无凭证无隐私数据。
   后续**不要**往这个仓库里放任何私密内容，否则等于公开发布。
4. **Pages 和 artifact 是两份独立产物**，改代码后两边都要推：
   `git push` 管 Pages，artifact 要重新 publish 到同一 URL（Artifact 工具传 `url` 参数）。
   只推一边会导致两个地址行为不一致。

## NEXT

1. 拿到用户实测结果 → 按 `TODO.md` 诊断对照表定位 → 关闭「进行中」那条，或按对应分支修。
2. 若 tilt 确认可用：问用户玩下来词库难度和回合时长合不合适，这是唯一需要真人反馈才能调的参数。
3. 若用户要继续加功能：优先「漏掉的词进下一局」，它对实际游戏体验的增益最大，改动也最小
   （`round.log` 里已经存了 `{w, got}`，数据结构不用动）。
