# Pixel Tetris

Lightweight Tetris prototype for fast game-logic and input debugging before an Android shell exists.

## Run

```sh
npm start
```

## Play On Android

Start the LAN server:

```sh
npm run start:phone
```

Open the printed `Phone URL` in Chrome on your Android phone. Keep the computer and phone on the same Wi-Fi network.

For a proper home-screen install with offline play, serve the same files from an HTTPS URL. The manifest and service worker are already included for that path. The LAN HTTP URL is the fastest way to play on a phone immediately.

## Test

```sh
npm test
```

## Scripted Play

```sh
npm run debug:play
npm run debug:play -- --seed debug --pieces 120 --verbose
```

The game is plain HTML, CSS, and JavaScript. It has no runtime dependencies and stores no generated assets in the repo.
