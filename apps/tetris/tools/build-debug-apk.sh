#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_NAME="com.premkr.pixeltetris"
APP_NAME="Pixel Tetris"
MIN_API="23"
TARGET_API="35"
BUILD_TOOLS_VERSION="35.0.1"

JAVA_HOME_AUTO="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")"
if [ -z "${JAVA_HOME:-}" ] || [ ! -x "${JAVA_HOME}/bin/javac" ]; then
  export JAVA_HOME="${JAVA_HOME_AUTO}"
fi

DEFAULT_SDK="${ANDROID_HOME:-$HOME/Android/Sdk}"
SDK_ROOT="${ANDROID_SDK_ROOT:-$DEFAULT_SDK}"
CMDLINE_SDK="${HOME}/Android/Sdk"

sdkmanager_bin() {
  if [ -x "${SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager" ]; then
    printf '%s\n' "${SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager"
  elif [ -x "${CMDLINE_SDK}/cmdline-tools/latest/bin/sdkmanager" ]; then
    printf '%s\n' "${CMDLINE_SDK}/cmdline-tools/latest/bin/sdkmanager"
  else
    return 1
  fi
}

has_sdk_packages() {
  [ -f "${SDK_ROOT}/platforms/android-${TARGET_API}/android.jar" ] &&
    [ -x "${SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}/aapt2" ] &&
    [ -x "${SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}/d8" ] &&
    [ -x "${SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}/zipalign" ] &&
    [ -x "${SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}/apksigner" ]
}

download_sdk_zip() {
  local url="$1"
  local destination="$2"
  mkdir -p "$(dirname "${destination}")"

  if [ -f "${destination}" ]; then
    echo "Using existing download: ${destination}"
    return
  fi

  echo "Downloading ${url}..."
  curl -L -o "${destination}" "${url}"
}

extract_single_root_to() {
  local zip_file="$1"
  local destination="$2"
  local temp_dir="${destination}.extract"

  rm -rf "${temp_dir}" "${destination}"
  mkdir -p "${temp_dir}" "${destination}"
  unzip -q "${zip_file}" -d "${temp_dir}"

  local root_dir
  root_dir="$(find "${temp_dir}" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  if [ -z "${root_dir}" ]; then
    echo "Could not find root directory in ${zip_file}" >&2
    exit 1
  fi

  mv "${root_dir}/"* "${destination}/"
  rm -rf "${temp_dir}"
}

install_sdk_packages_manually() {
  local download_dir="/tmp/pixel-tetris-sdk-downloads"
  local base_url="https://dl.google.com/android/repository"
  local platform_zip="${download_dir}/platform-35_r02.zip"
  local build_tools_zip="${download_dir}/build-tools_r35.0.1_linux.zip"
  local platform_tools_zip="${download_dir}/platform-tools_r37.0.0-linux.zip"

  mkdir -p "${SDK_ROOT}/platforms" "${SDK_ROOT}/build-tools"

  download_sdk_zip "${base_url}/platform-35_r02.zip" "${platform_zip}"
  download_sdk_zip "${base_url}/build-tools_r35.0.1_linux.zip" "${build_tools_zip}"
  download_sdk_zip "${base_url}/platform-tools_r37.0.0-linux.zip" "${platform_tools_zip}"

  extract_single_root_to "${platform_zip}" "${SDK_ROOT}/platforms/android-${TARGET_API}"
  extract_single_root_to "${build_tools_zip}" "${SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}"
  extract_single_root_to "${platform_tools_zip}" "${SDK_ROOT}/platform-tools"
}

ensure_sdk_packages() {
  if has_sdk_packages; then
    return
  fi

  local manager
  manager="$(sdkmanager_bin)" || {
    echo "sdkmanager not found. Run ./tools/install-android-sdk.sh first." >&2
    exit 1
  }

  if [ ! -w "${SDK_ROOT}" ]; then
    SDK_ROOT="/tmp/pixel-tetris-android-sdk"
    mkdir -p "${SDK_ROOT}"
  fi

  echo "Installing missing Android SDK packages into ${SDK_ROOT}..."
  set +e
  set +o pipefail
  yes | "${manager}" --sdk_root="${SDK_ROOT}" --licenses >/dev/null
  yes | "${manager}" --sdk_root="${SDK_ROOT}" \
    "platforms;android-${TARGET_API}" \
    "build-tools;${BUILD_TOOLS_VERSION}" \
    "platform-tools"
  local sdkmanager_status=$?
  set -o pipefail
  set -e

  if [ "${sdkmanager_status}" -ne 0 ] || ! has_sdk_packages; then
    echo "sdkmanager did not complete; falling back to direct SDK zip downloads."
    install_sdk_packages_manually
  fi

  if ! has_sdk_packages; then
    echo "Android SDK packages are still missing after install attempt." >&2
    exit 1
  fi
}

copy_web_assets() {
  local assets_dir="$1/www"
  rm -rf "$1"
  mkdir -p "${assets_dir}/src" "${assets_dir}/assets"

  cp "${ROOT}/index.html" "${assets_dir}/"
  cp "${ROOT}/manifest.webmanifest" "${assets_dir}/"
  cp "${ROOT}/sw.js" "${assets_dir}/"
  cp "${ROOT}/src/"*.js "${assets_dir}/src/"
  cp "${ROOT}/src/styles.css" "${assets_dir}/src/"
  cp "${ROOT}/assets/icon.svg" "${assets_dir}/assets/"
}

ensure_sdk_packages

export ANDROID_HOME="${SDK_ROOT}"
export ANDROID_SDK_ROOT="${SDK_ROOT}"
export PATH="${SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}:${SDK_ROOT}/platform-tools:${SDK_ROOT}/cmdline-tools/latest/bin:${PATH}"

ANDROID_JAR="${SDK_ROOT}/platforms/android-${TARGET_API}/android.jar"
AAPT2="${SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}/aapt2"
D8="${SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}/d8"
ZIPALIGN="${SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}/zipalign"
APKSIGNER="${SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}/apksigner"

BUILD_DIR="${ROOT}/build/android"
GEN_DIR="${BUILD_DIR}/gen"
CLASSES_DIR="${BUILD_DIR}/classes"
DEX_DIR="${BUILD_DIR}/dex"
RES_FLAT_DIR="${BUILD_DIR}/res-flat"
ASSETS_DIR="${BUILD_DIR}/assets"
OUT_DIR="${ROOT}/app/build/outputs/apk/debug"
UNSIGNED_APK="${BUILD_DIR}/app-unsigned.apk"
DEXED_APK="${BUILD_DIR}/app-unsigned-dex.apk"
ALIGNED_APK="${BUILD_DIR}/app-aligned.apk"
FINAL_APK="${OUT_DIR}/app-debug.apk"
KEYSTORE="${BUILD_DIR}/debug.keystore"

rm -rf "${BUILD_DIR}" "${OUT_DIR}"
mkdir -p "${GEN_DIR}" "${CLASSES_DIR}" "${DEX_DIR}" "${RES_FLAT_DIR}" "${OUT_DIR}"
copy_web_assets "${ASSETS_DIR}"

echo "Compiling Android resources..."
"${AAPT2}" compile --dir "${ROOT}/android/res" -o "${RES_FLAT_DIR}"

echo "Linking APK resources and web assets..."
"${AAPT2}" link \
  -I "${ANDROID_JAR}" \
  --manifest "${ROOT}/android/AndroidManifest.xml" \
  --java "${GEN_DIR}" \
  --min-sdk-version "${MIN_API}" \
  --target-sdk-version "${TARGET_API}" \
  --rename-manifest-package "${PACKAGE_NAME}" \
  -A "${ASSETS_DIR}" \
  -o "${UNSIGNED_APK}" \
  "${RES_FLAT_DIR}"/*.flat

echo "Compiling Java..."
javac -source 8 -target 8 \
  -classpath "${ANDROID_JAR}:${GEN_DIR}" \
  -d "${CLASSES_DIR}" \
  $(find "${ROOT}/android/src" "${GEN_DIR}" -name '*.java' | sort)

echo "Creating dex bytecode..."
"${D8}" --min-api "${MIN_API}" --lib "${ANDROID_JAR}" --output "${DEX_DIR}" $(find "${CLASSES_DIR}" -name '*.class' | sort)

cp "${UNSIGNED_APK}" "${DEXED_APK}"
zip -q -j "${DEXED_APK}" "${DEX_DIR}/classes.dex"

echo "Aligning APK..."
"${ZIPALIGN}" -f 4 "${DEXED_APK}" "${ALIGNED_APK}"

if [ ! -f "${KEYSTORE}" ]; then
  echo "Creating debug signing key..."
  keytool -genkeypair \
    -keystore "${KEYSTORE}" \
    -storepass android \
    -keypass android \
    -alias androiddebugkey \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -dname "CN=Android Debug,O=Android,C=US" \
    >/dev/null
fi

echo "Signing APK..."
"${APKSIGNER}" sign \
  --ks "${KEYSTORE}" \
  --ks-pass pass:android \
  --key-pass pass:android \
  --out "${FINAL_APK}" \
  "${ALIGNED_APK}"

"${APKSIGNER}" verify --verbose "${FINAL_APK}"

echo
echo "APK ready:"
echo "${FINAL_APK}"
