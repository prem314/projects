const KEY_ACTIONS = new Map([
  ["ArrowLeft", "left"],
  ["ArrowRight", "right"],
  ["ArrowDown", "down"],
  ["ArrowUp", "rotate"],
  ["KeyX", "rotate"],
  ["KeyZ", "rotateBack"],
  ["Space", "drop"],
  ["KeyP", "pause"],
  ["KeyR", "restart"],
  ["KeyB", "bot"]
]);

const HOLD_ACTIONS = new Set(["left", "right", "down"]);

export function bindKeyboard(actions) {
  window.addEventListener("keydown", (event) => {
    const action = KEY_ACTIONS.get(event.code);
    if (!action) return;

    event.preventDefault();
    actions[action]?.();
  });
}

export function bindButtons(root, actions) {
  for (const button of root.querySelectorAll("[data-action]")) {
    const action = button.dataset.action;
    let repeatId = 0;
    let delayId = 0;

    const stop = () => {
      window.clearTimeout(delayId);
      window.clearInterval(repeatId);
      delayId = 0;
      repeatId = 0;
    };

    button.addEventListener("pointerdown", (event) => {
      event.preventDefault();
      button.setPointerCapture?.(event.pointerId);
      actions[action]?.();

      if (HOLD_ACTIONS.has(action)) {
        delayId = window.setTimeout(() => {
          repeatId = window.setInterval(() => actions[action]?.(), action === "down" ? 52 : 82);
        }, 170);
      }
    });

    button.addEventListener("pointerup", stop);
    button.addEventListener("pointercancel", stop);
    button.addEventListener("lostpointercapture", stop);
    button.addEventListener("contextmenu", (event) => event.preventDefault());
  }
}
