#!/usr/bin/env bash
set -euo pipefail

REPO="amlife/aws-whats-new-pptx"
BRANCH="main"
SKILL_NAME="aws-whats-new-pptx"
INSTALL_DIR="$HOME/.kiro/skills/$SKILL_NAME"
GITHUB_BASE="https://github.com/$REPO"

# Download function that works with both curl and wget
download_file() {
  local url="$1"
  local output="$2"

  if [ "$DOWNLOADER" = "curl" ]; then
    if [ -n "$output" ]; then
      curl -fsSL -o "$output" "$url"
    else
      curl -fsSL "$url"
    fi
  elif [ "$DOWNLOADER" = "wget" ]; then
    if [ -n "$output" ]; then
      wget -q -O "$output" "$url"
    else
      wget -q -O - "$url"
    fi
  else
    return 1
  fi
}

main() {
  # Check for required dependencies
  DOWNLOADER=""
  if command -v curl >/dev/null 2>&1; then
    DOWNLOADER="curl"
  elif command -v wget >/dev/null 2>&1; then
    DOWNLOADER="wget"
  else
    echo "curl 또는 wget이 필요합니다." >&2
    exit 1
  fi

  echo "🔧 Kiro 스킬 설치: $SKILL_NAME"
  echo ""

  # Detect new install vs update
  if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 기존 설치를 업데이트합니다..."
    rm -rf "$INSTALL_DIR"
  else
    echo "📥 신규 설치를 진행합니다..."
  fi

  mkdir -p "$INSTALL_DIR"

  local TMP_DIR
  TMP_DIR=$(mktemp -d)
  trap 'rm -rf "$TMP_DIR"' EXIT

  # Prefer git clone (shallow), fallback to curl/wget tarball
  if command -v git >/dev/null 2>&1; then
    echo "📦 git clone으로 다운로드 중..."
    if ! git clone --depth 1 --branch "$BRANCH" "$GITHUB_BASE.git" "$TMP_DIR/repo" 2>/dev/null; then
      echo "git clone 실패" >&2
      exit 1
    fi
    local SRC="$TMP_DIR/repo/skills/$SKILL_NAME"
  else
    echo "📦 tarball로 다운로드 중..."
    local TARBALL="$TMP_DIR/archive.tar.gz"
    if ! download_file "$GITHUB_BASE/archive/refs/heads/$BRANCH.tar.gz" "$TARBALL"; then
      echo "다운로드 실패" >&2
      exit 1
    fi
    tar xzf "$TARBALL" -C "$TMP_DIR"
    local SRC="$TMP_DIR/$SKILL_NAME-$BRANCH/skills/$SKILL_NAME"
  fi

  # Verify essential files exist
  if [ ! -f "$SRC/SKILL.md" ]; then
    echo "SKILL.md를 찾을 수 없습니다. 리포지토리 구조를 확인하세요." >&2
    exit 1
  fi

  # Copy skill files
  echo "📂 스킬 파일을 복사합니다..."
  for item in SKILL.md assets references scripts; do
    if [ -e "$SRC/$item" ]; then
      cp -R "$SRC/$item" "$INSTALL_DIR/"
    fi
  done

  # Make scripts executable
  if [ -d "$INSTALL_DIR/scripts" ]; then
    find "$INSTALL_DIR/scripts" -name "*.sh" -exec chmod +x {} \;
  fi

  echo ""
  echo "✅ 설치 완료: $INSTALL_DIR"
  echo "   Kiro를 재시작하면 스킬이 활성화됩니다."
}

main "$@"
