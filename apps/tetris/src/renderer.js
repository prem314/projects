import { getPieceMatrix } from "./game.js";

const COLORS = Object.freeze({
  I: { main: "#31d7f4", dark: "#0f7386", light: "#baf6ff" },
  J: { main: "#4b7dff", dark: "#1d3f9e", light: "#c2d2ff" },
  L: { main: "#ff9f2d", dark: "#9f5518", light: "#ffe0ac" },
  O: { main: "#ffd84a", dark: "#9d7b13", light: "#fff1ac" },
  S: { main: "#49d66d", dark: "#1f7f3a", light: "#b9f4c9" },
  T: { main: "#b96aff", dark: "#6f2cab", light: "#e4c1ff" },
  Z: { main: "#ff5c70", dark: "#a52535", light: "#ffc0c8" }
});

function fitCanvas(canvas) {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const width = Math.max(1, Math.round(rect.width * dpr));
  const height = Math.max(1, Math.round(rect.height * dpr));

  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }

  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.imageSmoothingEnabled = false;
  return { ctx, width: rect.width, height: rect.height };
}

function drawCell(ctx, x, y, size, type, alpha = 1) {
  const color = COLORS[type];
  if (!color) return;

  const inset = Math.max(1, Math.floor(size * 0.1));
  const shine = Math.max(2, Math.floor(size * 0.18));

  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.fillStyle = color.dark;
  ctx.fillRect(x, y, size, size);
  ctx.fillStyle = color.main;
  ctx.fillRect(x + inset, y + inset, size - inset * 2, size - inset * 2);
  ctx.fillStyle = color.light;
  ctx.fillRect(x + inset, y + inset, size - inset * 2, shine);
  ctx.restore();
}

function drawGhostCell(ctx, x, y, size, type) {
  const color = COLORS[type];
  if (!color) return;

  const inset = Math.max(2, Math.floor(size * 0.14));
  ctx.save();
  ctx.globalAlpha = 0.42;
  ctx.strokeStyle = color.light;
  ctx.lineWidth = Math.max(1, Math.floor(size * 0.08));
  ctx.strokeRect(x + inset, y + inset, size - inset * 2, size - inset * 2);
  ctx.restore();
}

function drawPanelBackground(ctx, width, height) {
  ctx.fillStyle = "#10151a";
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = "#151d24";
  ctx.fillRect(4, 4, width - 8, height - 8);
}

export class BoardRenderer {
  constructor(canvas) {
    this.canvas = canvas;
  }

  render(snapshot) {
    const { ctx, width, height } = fitCanvas(this.canvas);
    ctx.clearRect(0, 0, width, height);
    drawPanelBackground(ctx, width, height);

    const cell = Math.floor(Math.min((width - 8) / snapshot.width, (height - 8) / snapshot.height));
    const boardWidth = cell * snapshot.width;
    const boardHeight = cell * snapshot.height;
    const left = Math.floor((width - boardWidth) / 2);
    const top = Math.floor((height - boardHeight) / 2);

    ctx.fillStyle = "#0b0e12";
    ctx.fillRect(left, top, boardWidth, boardHeight);

    ctx.strokeStyle = "#242b33";
    ctx.lineWidth = 1;
    for (let x = 0; x <= snapshot.width; x += 1) {
      const px = left + x * cell + 0.5;
      ctx.beginPath();
      ctx.moveTo(px, top);
      ctx.lineTo(px, top + boardHeight);
      ctx.stroke();
    }
    for (let y = 0; y <= snapshot.height; y += 1) {
      const py = top + y * cell + 0.5;
      ctx.beginPath();
      ctx.moveTo(left, py);
      ctx.lineTo(left + boardWidth, py);
      ctx.stroke();
    }

    for (const cellData of snapshot.ghostCells) {
      drawGhostCell(
        ctx,
        left + cellData.x * cell,
        top + cellData.y * cell,
        cell,
        cellData.type
      );
    }

    for (let y = 0; y < snapshot.height; y += 1) {
      for (let x = 0; x < snapshot.width; x += 1) {
        const type = snapshot.board[y][x];
        if (type) drawCell(ctx, left + x * cell, top + y * cell, cell, type);
      }
    }

    for (const cellData of snapshot.activeCells) {
      drawCell(ctx, left + cellData.x * cell, top + cellData.y * cell, cell, cellData.type);
    }

    if (snapshot.paused || snapshot.gameOver) {
      ctx.fillStyle = "rgba(5, 7, 10, 0.72)";
      ctx.fillRect(left, top, boardWidth, boardHeight);
      ctx.fillStyle = "#f6f0df";
      ctx.font = `700 ${Math.max(20, Math.floor(cell * 1.05))}px ui-monospace, Menlo, monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(snapshot.gameOver ? "Game Over" : "Paused", left + boardWidth / 2, top + boardHeight / 2);
    }
  }
}

export class PreviewRenderer {
  constructor(canvas) {
    this.canvas = canvas;
  }

  render(type) {
    const { ctx, width, height } = fitCanvas(this.canvas);
    ctx.clearRect(0, 0, width, height);
    drawPanelBackground(ctx, width, height);
    if (!type) return;

    const matrix = getPieceMatrix(type, 0);
    const rows = matrix.length;
    const cols = matrix[0].length;
    const cell = Math.floor(Math.min((width - 28) / Math.max(cols, 4), (height - 28) / Math.max(rows, 4)));
    const pieceWidth = cols * cell;
    const pieceHeight = rows * cell;
    const left = Math.floor((width - pieceWidth) / 2);
    const top = Math.floor((height - pieceHeight) / 2);

    for (let y = 0; y < rows; y += 1) {
      for (let x = 0; x < cols; x += 1) {
        if (matrix[y][x]) {
          drawCell(ctx, left + x * cell, top + y * cell, cell, type);
        }
      }
    }
  }
}
