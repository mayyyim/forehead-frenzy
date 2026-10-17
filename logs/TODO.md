# TODO — Forehead Frenzy（英文你比划我猜）

线上地址：https://claude.ai/artifact/XxgLQ8fHpYnQF1gVUYMfYA （Version 3）
源码：`index.html`（单文件，无依赖，无构建步骤。改完重新 publish 到同一 URL 即可）

## 进行中
- [ ] **验证 tilt 在 artifact iframe 里能不能用**（agent: 主 Claude，起始: 2026-10-17，状态: 代码已全部写完并上线，唯一未验证的是环境权限问题）
  下次打开第一步：问用户手机实测结果 —— 在手机浏览器打开上面的链接，点 `Enable tilt`：
  - **A. 出现实时倾斜条且翻手机会动** → 功能正常，无需任何改动，本任务可直接关闭
  - **B. 提示 `No sensor readings here`** → iframe 没放行传感器权限（`allow="accelerometer; gyroscope"`），
    此时唯一出路是把 `index.html` 部署到真实 HTTPS 顶层域名（Cloudflare Pages / Netlify drop，
    拖一个文件即可，无需构建）。**注意：本地 file:// 和局域网 http:// 都不行** ——
    iOS 的 `DeviceMotionEvent.requestPermission()` 要求 secure context，这是整个方案必须走 HTTPS 的根因。
  - **C. 倾斜条读数明显发飘/乱跳** → 说明走了降级路径（只有 deviceorientation 没有 devicemotion），
    `cos(beta)·cos(gamma)` 在贴额头姿态（beta≈90°）撞万向锁。改法：竖握玩，或切 Tap 模式。

## 待办
- [ ] 多选主题混合（现在只能单选一个 deck 或四个预设 mix）。优先级: 低 —— 四个 mix 大概够用了
- [ ] 词库按难度分 easy / hard 两档（现在全是 A1–B1 一档）。优先级: 低
- [ ] 回合结束后「漏掉的词」支持加入下一局重练。优先级: 低

## 已完成
- [x] 单文件网页游戏全功能上线（完成: 2026-10-17，无 git 仓库，版本以 artifact Version 号为准）
      翻转检测 / 3-2-1 倒计时 / 30-60-90-120s 计时 / 计分 + 逐词回看 / 分主题 best score（localStorage）
      / Tap 降级模式 / 屏幕常亮 / 震动 + WebAudio 音效 / 方向键桌面操作
- [x] 词库 450 → 1672 词，10 → 23 主题 + 4 个混合 deck（完成: 2026-10-17）

## 阻塞中
- [!] 无阻塞。上面「进行中」那条等的是用户手机实测结果，不是技术阻塞

---

## 关键设计决策（改代码前必读，否则容易踩回原坑）

**翻转检测用的是重力在屏幕法线（device z 轴）上的投影，不是 beta/gamma 角度。**
这不是随便选的，有两个硬理由，改之前想清楚：
1. **绕 z 轴旋转不改变 z 分量**（数学上恒等），所以竖握 / 横握 / 斜握都不影响判定，
   且完全不需要读 `screen.orientation`，系统旋转锁开关也不影响。
2. 贴额头的姿态正好是 `beta ≈ 90°`，**这是 Z-X'-Y'' 欧拉角的万向锁死区**，
   用角度判定会乱跳。z 分量绕开了这个问题。

**iOS 和 Android 的 `accelerationIncludingGravity` 符号相反**，所以有个自动校准：
趁用户在设置页拿着手机（`|beta|<60 且 |gamma|<60`，远离死区）时，
拿 `deviceorientation` 算出的 `cos(beta)·cos(gamma)` 符号去交叉验证加速度计的 z 符号，
结果存 `localStorage` 的 `ff.v1.sign`。兜底是界面上的 `Flip up/down` 按钮（存 `ff.v1.invert`）。

**阈值**：超过 0.60（离竖直约 37°）触发，必须回到 0.34 以内才接受下一次（防连击）。

## 本会话删除的东西
只删了我自己生成的临时脚本（`newdata.py` / `patch2.py` / `patch3.py` / `patch4.py` /
`check.js` / `data.js`，均在 session scratchpad 内）——
都是一次性的词库注入和语法校验脚本，产物已全部落进 `index.html`，无保留价值。
**没有删除任何项目文件、功能或文档**，所以不存在过期文档需要同步。
