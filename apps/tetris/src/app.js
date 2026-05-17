import { Game } from "./game.js";
import { chooseBotPlan, applyGameAction } from "./bot.js";
import { BoardRenderer, PreviewRenderer } from "./renderer.js";
import { bindButtons, bindKeyboard } from "./input.js";

const game = new Game({ seed: Date.now() });
const boardRenderer = new BoardRenderer(document.querySelector("#gameCanvas"));
const previewRenderer = new PreviewRenderer(document.querySelector("#nextCanvas"));

const scoreEl = document.querySelector("#score");
const linesEl = document.querySelector("#lines");
const levelEl = document.querySelector("#level");
const stateEl = document.querySelector("#state");
const pauseButton = document.querySelector("#pauseButton");
const botButton = document.querySelector("#botButton");

let botEnabled = false;
let botQueue = [];
let lastTime = performance.now();

function restart() {
  game.reset(Date.now());
  botQueue = [];
}

function setBot(enabled) {
  botEnabled = enabled;
  botQueue = [];
  botButton.classList.toggle("is-active", botEnabled);
  botButton.textContent = botEnabled ? "Bot On" : "Bot";
}

const actions = {
  left: () => game.move(-1),
  right: () => game.move(1),
  down: () => game.softDrop(),
  rotate: () => game.rotate(1),
  rotateBack: () => game.rotate(-1),
  drop: () => game.hardDrop(),
  pause: () => game.togglePause(),
  restart,
  bot: () => setBot(!botEnabled)
};

bindKeyboard(actions);
bindButtons(document, actions);

window.setInterval(() => {
  if (!botEnabled || game.paused || game.gameOver) return;
  if (botQueue.length === 0) {
    botQueue = chooseBotPlan(game);
  }
  const action = botQueue.shift();
  applyGameAction(game, action);
}, 70);

function updateHud(snapshot) {
  scoreEl.textContent = String(snapshot.score);
  linesEl.textContent = String(snapshot.lines);
  levelEl.textContent = String(snapshot.level);
  stateEl.textContent = snapshot.gameOver ? "Over" : snapshot.paused ? "Paused" : "Live";
  pauseButton.textContent = snapshot.paused ? ">" : "II";
}

function frame(now) {
  const delta = now - lastTime;
  lastTime = now;
  game.tick(delta);

  const snapshot = game.getSnapshot();
  boardRenderer.render(snapshot);
  previewRenderer.render(snapshot.next[0]);
  updateHud(snapshot);

  requestAnimationFrame(frame);
}

requestAnimationFrame(frame);

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {});
  });
}
