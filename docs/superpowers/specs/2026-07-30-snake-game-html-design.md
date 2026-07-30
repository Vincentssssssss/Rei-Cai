# 贪吃蛇小游戏设计文档（HTML/CSS/JS）

## 1. 目标与范围

在仓库中新增一个可独立运行的贪吃蛇小游戏，使用三文件结构：

- `snake.html`
- `snake.css`
- `snake.js`

运行方式为本地浏览器直接打开 `snake.html`，无需后端服务。

已确认需求约束：

- 渲染方案：Canvas（方案 1）
- 文件组织：三文件拆分
- 操作方式：仅键盘（方向键 + WASD）
- 游戏结束交互：`alert("Game Over")`，按空格重开

非目标（本次不做）：

- 手机触控按钮
- 排行榜、存档、联网
- 复杂特效（粒子、渐变动画、音效等）

## 2. 总体设计

采用“状态 + 定时循环 + Canvas 渲染”的最小可维护结构。

### 2.1 页面层（snake.html）

职责：

- 提供游戏标题、分数展示、操作提示
- 挂载一个固定尺寸的 `<canvas>`
- 引入 `snake.css` 和 `snake.js`

关键元素：

- `#score`：实时分数
- `#high-score`：最高分（本页会话内）
- `#game-canvas`：主游戏画布
- 简短说明文案（方向键/WASD，空格重开）

### 2.2 样式层（snake.css）

职责：

- 页面居中布局
- 深色背景 + 高对比配色
- Canvas 边框和信息卡样式

约束：

- 不依赖任何第三方 CSS 框架
- 保持纯静态资源，可脱离网络运行

### 2.3 逻辑层（snake.js）

职责：

- 维护游戏状态
- 处理键盘输入
- 执行主循环
- 绘制网格、蛇、食物
- 管理游戏结束与重开

## 3. 数据模型与状态

基础常量：

- `GRID_SIZE = 20`（20x20 网格）
- `CELL_SIZE = 20`（像素）
- `INITIAL_SPEED_MS = 140`
- `MIN_SPEED_MS = 70`
- `SPEED_STEP_MS = 4`

核心状态：

- `snake: Array<{x:number,y:number}>`（头在数组首位）
- `food: {x:number,y:number}`
- `direction: {x:number,y:number}`（当前方向）
- `nextDirection: {x:number,y:number}`（下一 tick 生效方向，避免连续按键错乱）
- `score: number`
- `highScore: number`
- `isGameOver: boolean`
- `tickMs: number`
- `loopTimer: number | null`

## 4. 游戏规则与流程

### 4.1 初始化

执行 `startGame()`：

1. 重置蛇身为 3 节（中部水平排列）
2. 默认向右移动
3. 置分数为 0，速度为初始值
4. 随机生成食物（确保不与蛇重叠）
5. 启动定时循环并渲染首帧

### 4.2 输入处理

监听 `keydown`：

- 映射：
  - `ArrowUp` / `W` -> 上
  - `ArrowDown` / `S` -> 下
  - `ArrowLeft` / `A` -> 左
  - `ArrowRight` / `D` -> 右
- 禁止 180 度反向（当前向右时不能立即向左）
- 游戏结束时按空格触发重开

### 4.3 每 tick 逻辑

1. 应用 `nextDirection`
2. 计算新蛇头坐标
3. 碰撞检测：
   - 越界：结束
   - 撞到自身：结束
4. 头插入蛇数组
5. 若吃到食物：
   - `score += 10`
   - 生成新食物
   - 按规则小幅加速（不低于最小速度）
6. 若未吃到食物：移除蛇尾
7. 重绘画布与分数

### 4.4 结束与重开

当发生死亡条件：

1. 停止循环
2. 维护最高分
3. 弹窗 `alert("Game Over! 得分: X。按空格重新开始。")`
4. 标记 `isGameOver = true`，等待空格

## 5. 渲染设计

每帧 `draw()`：

1. 清空画布背景
2. 绘制淡色网格线（提高方向感）
3. 绘制食物（红色方块）
4. 绘制蛇：
   - 头部与身体用不同色值区分
5. 更新 `#score` 与 `#high-score` 文本

## 6. 错误与边界处理

- 食物生成使用重试循环，直到找到非蛇身坐标
- 重开时确保销毁旧 `setInterval`，避免多循环叠加
- 仅处理必要键位，忽略其他键盘事件

## 7. 验证策略

手工验证项：

1. 打开 `snake.html`，页面正常显示
2. 方向键与 WASD 可控制移动
3. 蛇不能直接反向
4. 吃食物后分数增加且身体变长
5. 碰撞触发 Game Over 弹窗
6. Game Over 后按空格可重开
7. 连续多局不会出现多重加速或定时器叠加

## 8. 实施清单

1. 新建 `snake.html` 页面骨架
2. 新建 `snake.css` 完成样式
3. 新建 `snake.js` 实现完整玩法
4. 本地手工验证关键流程
