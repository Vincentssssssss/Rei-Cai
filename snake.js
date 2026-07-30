"use strict";

const GRID_SIZE = 20;
const CELL_SIZE = 20;
const INITIAL_SPEED_MS = 140;
const MIN_SPEED_MS = 70;
const SPEED_STEP_MS = 4;

const canvas = document.getElementById("game-canvas");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");
const highScoreEl = document.getElementById("high-score");

let snake = [];
let food = { x: 0, y: 0 };
let direction = { x: 1, y: 0 };
let nextDirection = { x: 1, y: 0 };
let score = 0;
let highScore = 0;
let isGameOver = false;
let tickMs = INITIAL_SPEED_MS;
let loopTimer = null;

function createInitialSnake() {
  const centerY = Math.floor(GRID_SIZE / 2);
  const startX = Math.floor(GRID_SIZE / 2);
  return [
    { x: startX, y: centerY },
    { x: startX - 1, y: centerY },
    { x: startX - 2, y: centerY },
  ];
}

function randomCell() {
  return Math.floor(Math.random() * GRID_SIZE);
}

function samePosition(a, b) {
  return a.x === b.x && a.y === b.y;
}

function isOnSnake(cell) {
  return snake.some((segment) => samePosition(segment, cell));
}

function spawnFood() {
  let candidate = { x: randomCell(), y: randomCell() };
  while (isOnSnake(candidate)) {
    candidate = { x: randomCell(), y: randomCell() };
  }
  food = candidate;
}

function updateScoreboard() {
  scoreEl.textContent = String(score);
  highScoreEl.textContent = String(highScore);
}

function clearLoop() {
  if (loopTimer !== null) {
    clearInterval(loopTimer);
    loopTimer = null;
  }
}

function startLoop() {
  clearLoop();
  loopTimer = setInterval(gameTick, tickMs);
}

function startGame() {
  snake = createInitialSnake();
  direction = { x: 1, y: 0 };
  nextDirection = { x: 1, y: 0 };
  score = 0;
  tickMs = INITIAL_SPEED_MS;
  isGameOver = false;
  spawnFood();
  updateScoreboard();
  draw();
  startLoop();
}

function isOppositeDirection(current, next) {
  return current.x + next.x === 0 && current.y + next.y === 0;
}

function handleDirectionKey(inputDirection) {
  if (!isOppositeDirection(direction, inputDirection)) {
    nextDirection = inputDirection;
  }
}

function handleKeyDown(event) {
  const key = event.key.toLowerCase();

  if (key === " " || key === "arrowup" || key === "arrowdown" || key === "arrowleft" || key === "arrowright") {
    event.preventDefault();
  }

  if (isGameOver && key === " ") {
    startGame();
    return;
  }

  const keyToDirection = {
    arrowup: { x: 0, y: -1 },
    w: { x: 0, y: -1 },
    arrowdown: { x: 0, y: 1 },
    s: { x: 0, y: 1 },
    arrowleft: { x: -1, y: 0 },
    a: { x: -1, y: 0 },
    arrowright: { x: 1, y: 0 },
    d: { x: 1, y: 0 },
  };

  const mapped = keyToDirection[key];
  if (mapped) {
    handleDirectionKey(mapped);
  }
}

function isWallCollision(head) {
  return head.x < 0 || head.y < 0 || head.x >= GRID_SIZE || head.y >= GRID_SIZE;
}

function isSelfCollision(head) {
  return snake.some((segment) => samePosition(segment, head));
}

function gameTick() {
  direction = nextDirection;
  const newHead = {
    x: snake[0].x + direction.x,
    y: snake[0].y + direction.y,
  };

  if (isWallCollision(newHead) || isSelfCollision(newHead)) {
    finishGame();
    return;
  }

  snake.unshift(newHead);

  if (samePosition(newHead, food)) {
    score += 10;
    if (score > highScore) {
      highScore = score;
    }
    spawnFood();

    if (tickMs > MIN_SPEED_MS) {
      tickMs = Math.max(MIN_SPEED_MS, tickMs - SPEED_STEP_MS);
      startLoop();
    }
  } else {
    snake.pop();
  }

  updateScoreboard();
  draw();
}

function finishGame() {
  clearLoop();
  if (score > highScore) {
    highScore = score;
  }
  updateScoreboard();
  draw();
  isGameOver = true;
  alert(`Game Over! 得分: ${score}。按空格重新开始。`);
}

function drawGrid() {
  ctx.strokeStyle = "#1e2940";
  ctx.lineWidth = 1;

  for (let i = 0; i <= GRID_SIZE; i += 1) {
    const pos = i * CELL_SIZE;

    ctx.beginPath();
    ctx.moveTo(pos, 0);
    ctx.lineTo(pos, canvas.height);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, pos);
    ctx.lineTo(canvas.width, pos);
    ctx.stroke();
  }
}

function drawCell(cell, color) {
  const padding = 1;
  ctx.fillStyle = color;
  ctx.fillRect(
    cell.x * CELL_SIZE + padding,
    cell.y * CELL_SIZE + padding,
    CELL_SIZE - padding * 2,
    CELL_SIZE - padding * 2
  );
}

function drawSnake() {
  snake.forEach((segment, index) => {
    drawCell(segment, index === 0 ? "#86f58f" : "#4ad66d");
  });
}

function drawFood() {
  drawCell(food, "#ff5d73");
}

function draw() {
  ctx.fillStyle = "#0f1320";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  drawGrid();
  drawFood();
  drawSnake();
}

document.addEventListener("keydown", handleKeyDown);
startGame();
