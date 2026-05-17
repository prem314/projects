import test from "node:test";
import assert from "node:assert/strict";
import { Game, boardFromRows } from "../src/game.js";
import { chooseBotPlan, applyGameAction } from "../src/bot.js";

test("seeded games start with the same active piece and queue", () => {
  const a = new Game({ seed: 1234 });
  const b = new Game({ seed: 1234 });

  assert.equal(a.active.type, b.active.type);
  assert.deepEqual(a.peekNext(5), b.peekNext(5));
});

test("movement cannot leave the board", () => {
  const game = new Game({ seed: 5 });

  for (let i = 0; i < 20; i += 1) game.move(-1);
  assert.ok(game.active.x >= 0);

  for (let i = 0; i < 20; i += 1) game.move(1);
  const rightEdge = game.active.x + game.active.matrix[0].length;
  assert.ok(rightEdge <= game.width);
});

test("hard drop locks cells and awards drop points", () => {
  const game = new Game({ seed: 10 });
  const type = game.active.type;

  const distance = game.hardDrop();

  assert.ok(distance > 0);
  assert.ok(game.score >= distance * 2);
  assert.ok(game.board.some((row) => row.includes(type)));
  assert.ok(game.active);
});

test("completed rows clear", () => {
  const game = new Game({ seed: 22 });
  game.board = boardFromRows([
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "..........",
    "IIIIIIIIII"
  ]);

  assert.equal(game.clearLines(), 1);
  assert.deepEqual(game.board[0], Array(game.width).fill(null));
  assert.equal(game.board.at(-1).join(""), "");
});

test("pause blocks player movement", () => {
  const game = new Game({ seed: 9 });
  const x = game.active.x;

  game.togglePause();
  assert.equal(game.move(-1), false);
  assert.equal(game.active.x, x);
});

test("bot can play several human-like action plans", () => {
  const game = new Game({ seed: 42 });

  for (let piece = 0; piece < 30 && !game.gameOver; piece += 1) {
    const plan = chooseBotPlan(game);
    assert.ok(plan.length > 0);
    assert.equal(plan.at(-1), "hardDrop");
    for (const action of plan) {
      applyGameAction(game, action);
    }
  }

  assert.equal(game.gameOver, false);
  assert.ok(game.score > 0);
});
