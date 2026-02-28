#!/usr/bin/env bash
set -euo pipefail

# 一鍵安裝：報告/簡報品質升級工具棧（WSL Ubuntu）
# 用法：
#   bash scripts/install-report-stack.sh
#   bash scripts/install-report-stack.sh --rollback

ROLLBACK="${1:-}"
LOG_DIR="$HOME/.openclaw/install-logs"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$LOG_DIR/report-stack-$STAMP.log"
mkdir -p "$LOG_DIR"

APT_PKGS=(
  fontconfig
  fonts-noto-cjk
  fonts-noto-color-emoji
  wkhtmltopdf
  python3-pip
  python3-venv
)

PIP_PKGS=(
  weasyprint
  jinja2
  matplotlib
  seaborn
  pandas
  openpyxl
  python-pptx
)

NPM_PKGS=(
  @marp-team/marp-cli
)

log(){ echo "[$(date +'%F %T')] $*" | tee -a "$LOG_FILE"; }

if [[ "$ROLLBACK" == "--rollback" ]]; then
  log "開始回滾（盡力而為）..."
  for p in "${PIP_PKGS[@]}"; do
    python3 -m pip uninstall -y "$p" --break-system-packages >/dev/null 2>&1 || true
    python3 -m pip uninstall -y "$p" --user >/dev/null 2>&1 || true
  done
  for p in "${NPM_PKGS[@]}"; do
    npm uninstall -g "$p" >/dev/null 2>&1 || true
  done
  if command -v sudo >/dev/null 2>&1; then
    sudo apt remove -y "${APT_PKGS[@]}" || true
    sudo apt autoremove -y || true
  fi
  log "回滾完成（部分系統依賴可能被其他軟體共用，故不一定會完全移除）。"
  exit 0
fi

log "開始安裝報告/簡報工具棧"
log "Log: $LOG_FILE"

if ! command -v sudo >/dev/null 2>&1; then
  log "找不到 sudo，請以可 sudo 帳號執行"
  exit 1
fi

log "APT 更新"
sudo apt update | tee -a "$LOG_FILE"

log "APT 安裝: ${APT_PKGS[*]}"
sudo apt install -y "${APT_PKGS[@]}" | tee -a "$LOG_FILE"

log "pip 安裝（user）: ${PIP_PKGS[*]}"
python3 -m pip install --user "${PIP_PKGS[@]}" | tee -a "$LOG_FILE"

if command -v npm >/dev/null 2>&1; then
  log "npm 全域安裝: ${NPM_PKGS[*]}"
  npm i -g "${NPM_PKGS[@]}" | tee -a "$LOG_FILE"
else
  log "未找到 npm，跳過 Marp 安裝"
fi

log "重建字體快取"
fc-cache -f -v >/dev/null 2>&1 || true

log "安裝完成。建議驗證："
log "  marp --version"
log "  python3 -c 'import weasyprint, pptx; print(""ok"")'"
log "  fc-list :lang=zh | head"
