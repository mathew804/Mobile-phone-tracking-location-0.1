# ╔══════════════════════════════════════════════════════════╗
#   MobilNumTrack — Makefile
#   Usage:  make install   →  install all dependencies
#           make run       →  launch the tracker
#           make update    →  pull latest from GitHub
#           make clean     →  remove cache files
# ╚══════════════════════════════════════════════════════════╝

PYTHON    := python3
PIP       := pip3
SCRIPT    := MobilNumTrack.py
REQS      := requirements.txt
GITHUB    := https://github.com/yourusername/MobilNumTrack.git

.PHONY: all install run update clean help

all: install run

## install — install all Python dependencies (no login, no key needed)
install:
	@echo "\033[96m[*] Installing dependencies ...\033[0m"
	@$(PIP) install -r $(REQS) --break-system-packages 2>/dev/null || \
	 $(PIP) install -r $(REQS) --quiet
	@echo "\033[92m[✔] Dependencies installed.\033[0m"

## run — launch MobilNumTrack
run:
	@$(PYTHON) $(SCRIPT)

## update — pull latest version from GitHub (no credentials required — public repo)
update:
	@echo "\033[96m[*] Pulling latest from GitHub (no login needed — public repo) ...\033[0m"
	@git pull --rebase 2>/dev/null && \
	 $(PIP) install -r $(REQS) --break-system-packages --quiet 2>/dev/null || \
	 $(PIP) install -r $(REQS) --quiet
	@echo "\033[92m[✔] Update complete. Run:  make run\033[0m"

## clean — remove Python cache files
clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	 find . -name "*.pyc" -delete 2>/dev/null; \
	 echo "\033[92m[✔] Cache cleaned.\033[0m"

## help — show this help message
help:
	@echo ""
	@echo "  \033[96mMobilNumTrack — Makefile Commands\033[0m"
	@echo ""
	@echo "  \033[93mmake install\033[0m   Install Python dependencies"
	@echo "  \033[93mmake run\033[0m       Launch MobilNumTrack"
	@echo "  \033[93mmake update\033[0m    Pull latest from GitHub (no login needed)"
	@echo "  \033[93mmake clean\033[0m     Remove cache files"
	@echo "  \033[93mmake all\033[0m       Install + Run in one command"
	@echo ""
