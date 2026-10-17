# TODO — Forehead Frenzy（英文你比划我猜）

**今晚用这个地址**：https://mayyyim.github.io/forehead-frenzy/ ← 顶层 HTTPS，传感器不被拦
备用（功能相同，但在 iframe 里，tilt 可能不工作）：https://claude.ai/artifact/XxgLQ8fHpYnQF1gVUYMfYA

源码：`index.html`（单文件，无依赖无构建）。改完 `git push` 即自动重新部署 Pages。
仓库：https://github.com/mayyyim/forehead-frenzy （public，Pages 免费版要求 public）

## 进行中
- [ ] **验证 GitHub Pages 上 tilt 是否正常**（agent: 主 Claude，起始: 2026-10-17）
  下次打开第一步：问用户在 https://mayyyim.github.io/forehead-frenzy/ 上点 `Enable tilt` 的结果。
  设置页底部现在有一行实时诊断读数，直接照着念就能定位：
  - `embedded:no (top level)` + `permission:granted` + `events:` 持续增长 → **正常**，本条可关闭
  - `permission:denied` → iOS 设置 › 应用 › Safari › 动作与方向访问 打开后重载
  - `permission:rejected (NotAllowedError)` → 权限请求被拒，通常是非 secure context
  - `events:0` 但 permission 是 granted → 传感器事件被过滤（iframe 场景）
  - 倾斜条方向相反 → 点 `Flip up/down`（存 `ff.v1.invert`）

## 待办
- [ ] 多选主题自由组合（现在是单选 23 主题之一，或 4 个预设 mix）。优先级: 低
- [ ] 词库分 easy / hard 两档。优先级: 低
- [ ] 回合结束后把漏掉的词加入下一局重练。优先级: 低

## 已完成
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

## 关键设计决策（改代码前必读）

**翻转检测用重力在屏幕法线（device z 轴）上的投影，不是 beta/gamma 角度。**两个硬理由：
1. **绕 z 轴旋转不改变 z 分量**（数学恒等）→ 竖握横握斜握都一样，且全程不读
   `screen.orientation`，系统旋转锁开关不影响。
2. 贴额头是 `beta ≈ 90°`，**正好是 Z-X'-Y'' 欧拉角的万向锁死区**，角度判定会乱跳。

**iOS 与 Android 的 `accelerationIncludingGravity` 符号相反** → 自动校准：
趁手机在设置页被拿在手里（`|beta|<60 且 |gamma|<60`，远离死区）时，
用 `cos(beta)·cos(gamma)` 的符号交叉验证加速度计 z 的符号，结果存 `ff.v1.sign`。
兜底是界面上的 `Flip up/down`（存 `ff.v1.invert`）。

**阈值**：超过 0.60（离竖直约 37°）触发，回到 0.34 以内才接受下一次。

**必须 HTTPS 且必须顶层页面**：iOS 的 `DeviceMotionEvent.requestPermission()` 要求
secure context（所以 `file://` 和局域网 `http://` 都不行），而 iframe 还需要父页面带
`allow="accelerometer; gyroscope"`（所以 artifact 里不行）。GitHub Pages 两个条件都满足。
