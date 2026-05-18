#!/usr/bin/env bash
set -euo pipefail

SDK_ROOT="${ANDROID_HOME:-$HOME/Android/Sdk}"
CMDLINE_VERSION="14742923"
CMDLINE_ZIP="commandlinetools-linux-${CMDLINE_VERSION}_latest.zip"
CMDLINE_URL="https://dl.google.com/android/repository/${CMDLINE_ZIP}"
DOWNLOAD_DIR="${TMPDIR:-/tmp}/android-sdk-install"

echo "Installing Android command-line build tools"
echo "SDK root: ${SDK_ROOT}"
echo

echo "Installing JDK/compiler and basic tools via apt..."
sudo apt update
sudo apt install --no-install-recommends -y openjdk-21-jdk-headless unzip curl

mkdir -p "${SDK_ROOT}/cmdline-tools" "${DOWNLOAD_DIR}"

cd "${DOWNLOAD_DIR}"
if [ ! -f "${CMDLINE_ZIP}" ]; then
  echo "Downloading Android command-line tools..."
  curl -L -o "${CMDLINE_ZIP}" "${CMDLINE_URL}"
else
  echo "Using existing download: ${DOWNLOAD_DIR}/${CMDLINE_ZIP}"
fi

rm -rf "${DOWNLOAD_DIR}/cmdline-tools-expanded"
mkdir -p "${DOWNLOAD_DIR}/cmdline-tools-expanded"
unzip -q "${CMDLINE_ZIP}" -d "${DOWNLOAD_DIR}/cmdline-tools-expanded"

rm -rf "${SDK_ROOT}/cmdline-tools/latest"
mkdir -p "${SDK_ROOT}/cmdline-tools/latest"
mv "${DOWNLOAD_DIR}/cmdline-tools-expanded/cmdline-tools/"* "${SDK_ROOT}/cmdline-tools/latest/"

export ANDROID_HOME="${SDK_ROOT}"
export ANDROID_SDK_ROOT="${SDK_ROOT}"
export PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${PATH}"
export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")"

if ! grep -q 'ANDROID_HOME="$HOME/Android/Sdk"' "$HOME/.bashrc"; then
  echo "Adding Android SDK environment variables to ~/.bashrc..."
  cat >> "$HOME/.bashrc" <<'EOF'

export ANDROID_HOME="$HOME/Android/Sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
EOF
fi

echo "Accepting Android SDK licenses..."
set +o pipefail
yes | sdkmanager --sdk_root="${ANDROID_HOME}" --licenses >/dev/null
set -o pipefail

echo "Installing minimal Android SDK packages..."
set +o pipefail
yes | sdkmanager --sdk_root="${ANDROID_HOME}" \
  "platforms;android-35" \
  "build-tools;35.0.1" \
  "platform-tools"
set -o pipefail

echo
echo "Done."
echo "Verify with:"
echo "  javac -version"
echo "  sdkmanager --version"
echo
echo "For this terminal session, run:"
echo "  export ANDROID_HOME=\"${SDK_ROOT}\""
echo "  export ANDROID_SDK_ROOT=\"${SDK_ROOT}\""
echo "  export PATH=\"${SDK_ROOT}/cmdline-tools/latest/bin:${SDK_ROOT}/platform-tools:\$PATH\""
echo "  export JAVA_HOME=\"${JAVA_HOME}\""
