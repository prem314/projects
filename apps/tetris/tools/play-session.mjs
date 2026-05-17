#!/usr/bin/env node
import { Game } from "../src/game.js";
import { chooseBotPlan, applyGameAction } from "../src/bot.js";

function readArg(name, fallback) {
  const index = process.argv.indexOf(`--${name}`);
  if (index === -1) return fallback;
  return process.argv[index + 1] ?? fallback;
}

const seed = readArg("seed", "debug");
const pieces = Number(readArg("pieces", "80"));
const verbose = process.argv.includes("--verbose");
const game = new Game({ seed });

for (let i = 0; i < pieces && !game.gameOver; i += 1) {
  const type = game.active.type;
  const plan = chooseBotPlan(game);
  if (verbose) {
    console.log(`${String(i + 1).padStart(3, "0")} ${type}: ${plan.join(" ")}`);
  }
  for (const action of plan) {
    applyGameAction(game, action);
  }
}

console.log(`seed=${seed}`);
console.log(`score=${game.score} lines=${game.lines} level=${game.level} gameOver=${game.gameOver}`);
console.log(game.serializeBoard({ active: true }));
