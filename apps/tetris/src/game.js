export const BOARD_WIDTH = 10;
export const BOARD_HEIGHT = 20;

export const PIECE_TYPES = Object.freeze(["I", "J", "L", "O", "S", "T", "Z"]);

const BASE_SHAPES = Object.freeze({
  I: Object.freeze([[1, 1, 1, 1]]),
  J: Object.freeze([
    [1, 0, 0],
    [1, 1, 1]
  ]),
  L: Object.freeze([
    [0, 0, 1],
    [1, 1, 1]
  ]),
  O: Object.freeze([
    [1, 1],
    [1, 1]
  ]),
  S: Object.freeze([
    [0, 1, 1],
    [1, 1, 0]
  ]),
  T: Object.freeze([
    [0, 1, 0],
    [1, 1, 1]
  ]),
  Z: Object.freeze([
    [1, 1, 0],
    [0, 1, 1]
  ])
});

const LINE_POINTS = Object.freeze({
  0: 0,
  1: 100,
  2: 300,
  3: 500,
  4: 800
});

function cloneMatrix(matrix) {
  return matrix.map((row) => row.slice());
}

export function createEmptyBoard(width = BOARD_WIDTH, height = BOARD_HEIGHT) {
  return Array.from({ length: height }, () => Array(width).fill(null));
}

export function boardFromRows(rows) {
  return rows.map((row) =>
    [...row].map((cell) => {
      if (cell === "." || cell === " ") return null;
      if (!PIECE_TYPES.includes(cell)) {
        throw new Error(`Unknown board cell: ${cell}`);
      }
      return cell;
    })
  );
}

export function rotateMatrix(matrix, direction = 1) {
  const rows = matrix.length;
  const cols = matrix[0].length;
  const rotated = [];

  if (direction >= 0) {
    for (let x = 0; x < cols; x += 1) {
      const row = [];
      for (let y = rows - 1; y >= 0; y -= 1) {
        row.push(matrix[y][x]);
      }
      rotated.push(row);
    }
  } else {
    for (let x = cols - 1; x >= 0; x -= 1) {
      const row = [];
      for (let y = 0; y < rows; y += 1) {
        row.push(matrix[y][x]);
      }
      rotated.push(row);
    }
  }

  return rotated;
}

export function getPieceMatrix(type, rotation = 0) {
  if (!BASE_SHAPES[type]) {
    throw new Error(`Unknown piece type: ${type}`);
  }

  let matrix = cloneMatrix(BASE_SHAPES[type]);
  const turns = ((rotation % 4) + 4) % 4;
  for (let i = 0; i < turns; i += 1) {
    matrix = rotateMatrix(matrix, 1);
  }
  return matrix;
}

function cellsFor(piece, matrix = piece.matrix, x = piece.x, y = piece.y) {
  const cells = [];
  for (let row = 0; row < matrix.length; row += 1) {
    for (let col = 0; col < matrix[row].length; col += 1) {
      if (matrix[row][col]) {
        cells.push({ x: x + col, y: y + row, type: piece.type });
      }
    }
  }
  return cells;
}

function hashSeed(seed) {
  if (typeof seed === "number" && Number.isFinite(seed)) {
    return seed >>> 0;
  }

  const text = String(seed ?? Date.now());
  let hash = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

export class Game {
  constructor(options = {}) {
    this.width = options.width ?? BOARD_WIDTH;
    this.height = options.height ?? BOARD_HEIGHT;
    this.reset(options.seed ?? Date.now());
  }

  reset(seed = Date.now()) {
    this.seed = hashSeed(seed);
    this.randomState = this.seed || 1;
    this.board = createEmptyBoard(this.width, this.height);
    this.bag = [];
    this.active = null;
    this.score = 0;
    this.lines = 0;
    this.level = 1;
    this.paused = false;
    this.gameOver = false;
    this.dropAccumulator = 0;
    this.lastClear = 0;
    this.ensureBag(7);
    this.spawnNext();
  }

  clone() {
    const copy = Object.create(Game.prototype);
    copy.width = this.width;
    copy.height = this.height;
    copy.seed = this.seed;
    copy.randomState = this.randomState;
    copy.board = this.board.map((row) => row.slice());
    copy.bag = this.bag.slice();
    copy.active = this.active
      ? { ...this.active, matrix: cloneMatrix(this.active.matrix) }
      : null;
    copy.score = this.score;
    copy.lines = this.lines;
    copy.level = this.level;
    copy.paused = this.paused;
    copy.gameOver = this.gameOver;
    copy.dropAccumulator = this.dropAccumulator;
    copy.lastClear = this.lastClear;
    return copy;
  }

  nextRandom() {
    this.randomState = (this.randomState + 0x6d2b79f5) >>> 0;
    let value = this.randomState;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  }

  ensureBag(count = 1) {
    while (this.bag.length < count) {
      const nextBag = PIECE_TYPES.slice();
      for (let i = nextBag.length - 1; i > 0; i -= 1) {
        const j = Math.floor(this.nextRandom() * (i + 1));
        [nextBag[i], nextBag[j]] = [nextBag[j], nextBag[i]];
      }
      this.bag.push(...nextBag);
    }
  }

  takeNextType() {
    this.ensureBag(1);
    const type = this.bag.shift();
    this.ensureBag(5);
    return type;
  }

  peekNext(count = 3) {
    this.ensureBag(count);
    return this.bag.slice(0, count);
  }

  spawnNext() {
    const type = this.takeNextType();
    const matrix = getPieceMatrix(type, 0);
    this.active = {
      type,
      rotation: 0,
      matrix,
      x: Math.floor((this.width - matrix[0].length) / 2),
      y: 0
    };

    if (this.collides(this.active)) {
      this.gameOver = true;
    }
  }

  get dropInterval() {
    return Math.max(85, 760 - (this.level - 1) * 55);
  }

  get isPlaying() {
    return !this.paused && !this.gameOver && Boolean(this.active);
  }

  tick(deltaMs) {
    if (!this.isPlaying) return false;

    this.dropAccumulator += deltaMs;
    let changed = false;
    while (this.dropAccumulator >= this.dropInterval && this.isPlaying) {
      const moved = this.step();
      this.dropAccumulator -= this.dropInterval;
      changed = true;
      if (!moved) break;
    }
    return changed;
  }

  collides(piece) {
    for (const cell of cellsFor(piece)) {
      if (cell.x < 0 || cell.x >= this.width || cell.y >= this.height) {
        return true;
      }
      if (cell.y >= 0 && this.board[cell.y][cell.x]) {
        return true;
      }
    }
    return false;
  }

  tryActive(active) {
    if (this.collides(active)) return false;
    this.active = active;
    return true;
  }

  move(dx) {
    if (!this.isPlaying) return false;
    return this.tryActive({ ...this.active, x: this.active.x + dx });
  }

  step() {
    if (!this.isPlaying) return false;
    const moved = this.tryActive({ ...this.active, y: this.active.y + 1 });
    if (!moved) {
      this.lockPiece();
    }
    return moved;
  }

  softDrop() {
    if (!this.isPlaying) return false;
    const moved = this.tryActive({ ...this.active, y: this.active.y + 1 });
    if (moved) {
      this.score += 1;
      return true;
    }
    this.lockPiece();
    return false;
  }

  hardDrop() {
    if (!this.isPlaying) return 0;

    let distance = 0;
    while (this.tryActive({ ...this.active, y: this.active.y + 1 })) {
      distance += 1;
    }
    this.score += distance * 2;
    this.lockPiece();
    return distance;
  }

  rotate(direction = 1) {
    if (!this.isPlaying) return false;
    const nextRotation = (this.active.rotation + (direction >= 0 ? 1 : -1) + 4) % 4;
    const matrix = getPieceMatrix(this.active.type, nextRotation);
    const kicks = [
      { x: 0, y: 0 },
      { x: -1, y: 0 },
      { x: 1, y: 0 },
      { x: -2, y: 0 },
      { x: 2, y: 0 },
      { x: 0, y: -1 },
      { x: -1, y: -1 },
      { x: 1, y: -1 }
    ];

    for (const kick of kicks) {
      const candidate = {
        ...this.active,
        rotation: nextRotation,
        matrix,
        x: this.active.x + kick.x,
        y: this.active.y + kick.y
      };
      if (this.tryActive(candidate)) {
        return true;
      }
    }
    return false;
  }

  lockPiece() {
    if (!this.active) return;

    for (const cell of cellsFor(this.active)) {
      if (cell.y < 0) {
        this.gameOver = true;
        return;
      }
      this.board[cell.y][cell.x] = cell.type;
    }

    this.lastClear = this.clearLines();
    if (this.lastClear > 0) {
      this.score += LINE_POINTS[this.lastClear] * this.level;
      this.lines += this.lastClear;
      this.level = Math.floor(this.lines / 10) + 1;
    }

    this.spawnNext();
    this.dropAccumulator = 0;
  }

  clearLines() {
    const remaining = this.board.filter((row) => row.some((cell) => !cell));
    const cleared = this.height - remaining.length;
    while (remaining.length < this.height) {
      remaining.unshift(Array(this.width).fill(null));
    }
    this.board = remaining;
    return cleared;
  }

  ghostY() {
    if (!this.active) return 0;
    let y = this.active.y;
    while (!this.collides({ ...this.active, y: y + 1 })) {
      y += 1;
    }
    return y;
  }

  activeCells() {
    if (!this.active) return [];
    return cellsFor(this.active).filter((cell) => cell.y >= 0);
  }

  ghostCells() {
    if (!this.active) return [];
    return cellsFor(this.active, this.active.matrix, this.active.x, this.ghostY()).filter(
      (cell) => cell.y >= 0
    );
  }

  getSnapshot() {
    return {
      width: this.width,
      height: this.height,
      board: this.board.map((row) => row.slice()),
      active: this.active ? { ...this.active, matrix: cloneMatrix(this.active.matrix) } : null,
      activeCells: this.activeCells(),
      ghostCells: this.ghostCells(),
      next: this.peekNext(3),
      score: this.score,
      lines: this.lines,
      level: this.level,
      paused: this.paused,
      gameOver: this.gameOver
    };
  }

  togglePause() {
    if (this.gameOver) return this.paused;
    this.paused = !this.paused;
    return this.paused;
  }

  serializeBoard({ active = true } = {}) {
    const rows = this.board.map((row) => row.map((cell) => cell ?? "."));
    if (active) {
      for (const cell of this.activeCells()) {
        rows[cell.y][cell.x] = cell.type;
      }
    }
    return rows.map((row) => row.join("")).join("\n");
  }
}
