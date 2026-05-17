function columnStats(board) {
  const height = board.length;
  const width = board[0].length;
  const heights = Array(width).fill(0);
  let holes = 0;

  for (let x = 0; x < width; x += 1) {
    let foundBlock = false;
    for (let y = 0; y < height; y += 1) {
      if (board[y][x]) {
        if (!foundBlock) {
          heights[x] = height - y;
          foundBlock = true;
        }
      } else if (foundBlock) {
        holes += 1;
      }
    }
  }

  let bumpiness = 0;
  for (let x = 0; x < width - 1; x += 1) {
    bumpiness += Math.abs(heights[x] - heights[x + 1]);
  }

  return {
    aggregateHeight: heights.reduce((sum, value) => sum + value, 0),
    maxHeight: Math.max(...heights),
    holes,
    bumpiness
  };
}

function matrixKey(matrix) {
  return matrix.map((row) => row.join("")).join("/");
}

function scoreBoard(game) {
  const stats = columnStats(game.board);
  return (
    game.lastClear * 22 -
    stats.aggregateHeight * 0.52 -
    stats.maxHeight * 0.9 -
    stats.holes * 7.5 -
    stats.bumpiness * 0.45
  );
}

export function chooseBotPlan(game) {
  if (!game.active || game.paused || game.gameOver) return [];

  let best = null;
  const seenRotations = new Set();

  for (let turns = 0; turns < 4; turns += 1) {
    const rotated = game.clone();
    for (let i = 0; i < turns; i += 1) {
      rotated.rotate(1);
    }

    const key = matrixKey(rotated.active.matrix);
    if (seenRotations.has(key)) continue;
    seenRotations.add(key);

    for (let targetX = -2; targetX < game.width + 2; targetX += 1) {
      const sim = rotated.clone();
      sim.active = { ...sim.active, x: targetX };
      if (sim.collides(sim.active)) continue;

      sim.hardDrop();
      const value = scoreBoard(sim);
      if (!best || value > best.value) {
        const actions = [];
        for (let i = 0; i < turns; i += 1) actions.push("rotate");

        const dx = targetX - rotated.active.x;
        const move = dx < 0 ? "left" : "right";
        for (let i = 0; i < Math.abs(dx); i += 1) actions.push(move);

        actions.push("hardDrop");
        best = { value, actions };
      }
    }
  }

  return best?.actions ?? ["hardDrop"];
}

export function applyGameAction(game, action) {
  switch (action) {
    case "left":
      return game.move(-1);
    case "right":
      return game.move(1);
    case "down":
      return game.softDrop();
    case "rotate":
      return game.rotate(1);
    case "rotateBack":
      return game.rotate(-1);
    case "hardDrop":
      return game.hardDrop();
    default:
      return false;
  }
}
