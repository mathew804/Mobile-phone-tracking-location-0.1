#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════╗
#   MobilNumTrack v4.0 — Auto Installer
#   Works on: Kali Linux, Parrot, Ubuntu, Debian, macOS, Termux
#   NO git clone needed. NO username. NO password. NO token. Ever.
#   Just run this script from inside the MobilNumTrack folder.
# ╚══════════════════════════════════════════════════════════════════════╝

R='\033[91m'; G='\033[92m'; Y='\033[93m'
C='\033[96m'; W='\033[97m'; BD='\033[1m'; RS='\033[0m'

clear
echo -e "${C}${BD}"
cat << 'BANNER'
  ╔═══════════════════════════════════════════════════════════╗
  ║  ███╗   ███╗ ██████╗ ██████╗ ██╗██╗                      ║
  ║  ████╗ ████║██╔═══██╗██╔══██╗██║██║                      ║
  ║  ██╔████╔██║██║   ██║██████╔╝██║██║                      ║
  ║  ██║╚██╔╝██║██║   ██║██╔══██╗██║██║                      ║
  ║  ██║ ╚═╝ ██║╚██████╔╝██████╔╝██║███████╗                 ║
  ║  ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═╝╚══════╝                 ║
  ║     NUM TRACK  v4.0  —  Installer                        ║
  ║     NO username • NO password • NO token                 ║
  ╚═══════════════════════════════════════════════════════════╝
BANNER
echo -e "${RS}"

# ── Detect platform ────────────────────────────────────────────────────────────
IS_TERMUX=false; IS_MACOS=false; IS_DEBIAN=false

if   [ -d "/data/data/com.termux" ]; then IS_TERMUX=true; echo -e "  ${Y}[*]${RS} Termux / Android"
elif [[ "$OSTYPE" == "darwin"* ]];   then IS_MACOS=true;  echo -e "  ${Y}[*]${RS} macOS"
else IS_DEBIAN=true; echo -e "  ${Y}[*]${RS} Linux (Kali / Ubuntu / Debian / Parrot)"
fi
echo ""

# ── [1/3] Python 3 ─────────────────────────────────────────────────────────────
echo -e "  ${C}[1/3]${RS} Checking Python 3 ..."
if command -v python3 &>/dev/null; then
    echo -e "       ${G}✔  $(python3 --version)${RS}"
else
    echo -e "       ${Y}⚠  Installing Python 3 ...${RS}"
    if $IS_TERMUX; then pkg install python -y
    elif $IS_MACOS; then brew install python3
    else sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip; fi
fi

# ── [2/3] Python packages ───────────────────────────────────────────────────────
echo -e "\n  ${C}[2/3]${RS} Installing Python packages ..."
# Try modern pip flag first (Kali 2024+ / Debian 12+), fall back to plain pip
python3 -m pip install phonenumbers requests pytz --quiet --break-system-packages 2>/dev/null \
  || python3 -m pip install phonenumbers requests pytz --quiet \
  || pip3 install phonenumbers requests pytz
echo -e "       ${G}✔  phonenumbers  requests  pytz — installed${RS}"

# ── [3/3] Permissions ──────────────────────────────────────────────────────────
echo -e "\n  ${C}[3/3]${RS} Setting permissions ..."
chmod +x MobilNumTrack.py install.sh 2>/dev/null
echo -e "       ${G}✔  Done${RS}"

# ── Done ───────────────────────────────────────────────────────────────────────
echo -e "\n${G}${BD}"
echo "  ╔═══════════════════════════════════════════════════════╗"
echo "  ║   ✔  MobilNumTrack v4.0 is ready!                   ║"
echo "  ║   No username • No password • No token               ║"
echo "  ╚═══════════════════════════════════════════════════════╝"
echo -e "${RS}"
echo -e "  ${Y}▶  Launch now:${RS}"
echo -e "     ${C}python3 MobilNumTrack.py${RS}"
echo ""
