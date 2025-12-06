PLUGIN_NAME := measure-annotate
SRC_DIR := src/$(PLUGIN_NAME)

# Auto-detect GIMP plugin directory (native vs Flatpak)
GIMP_NATIVE := $(HOME)/.config/GIMP/3.0
GIMP_FLATPAK := $(HOME)/.var/app/org.gimp.GIMP/config/GIMP/3.0

GIMP_CONFIG := $(shell test -d $(GIMP_NATIVE) && echo $(GIMP_NATIVE) || \
                      (test -d $(GIMP_FLATPAK) && echo $(GIMP_FLATPAK)))
GIMP_PLUGIN_DIR := $(GIMP_CONFIG)/plug-ins

.PHONY: check dev install uninstall clean help

help:
	@echo "GIMP Measure Annotate Plugin"
	@echo ""
	@echo "Targets:"
	@echo "  make dev       - Install as symlink (for development)"
	@echo "  make install   - Install as copy (for production)"
	@echo "  make uninstall - Remove plugin from GIMP"
	@echo "  make check     - Verify GIMP 3.x installation"
	@echo ""
	@echo "After install, restart GIMP and assign keyboard shortcuts via:"
	@echo "  Edit → Preferences → Interface → Keyboard Shortcuts"
	@echo ""
	@echo "Search for 'measure' to find:"
	@echo "  - Measure Horizontal (suggested: Ctrl+Shift+H)"
	@echo "  - Measure Vertical   (suggested: Ctrl+Shift+V)"
	@echo "  - Measure Diagonal   (suggested: Ctrl+Shift+D)"

check:
	@test -n "$(GIMP_CONFIG)" || \
		(echo "Error: GIMP 3.x config not found." && \
		 echo "Checked:" && \
		 echo "  - $(GIMP_NATIVE)" && \
		 echo "  - $(GIMP_FLATPAK)" && \
		 echo "" && \
		 echo "Please install GIMP 3.x and run it once to create config directory." && \
		 exit 1)
	@echo "Detected GIMP config: $(GIMP_CONFIG)"

dev: check
	@mkdir -p $(GIMP_PLUGIN_DIR)
	@ln -sfn $(CURDIR)/$(SRC_DIR) $(GIMP_PLUGIN_DIR)/$(PLUGIN_NAME)
	@chmod +x $(SRC_DIR)/$(PLUGIN_NAME).py
	@echo "Dev install complete (symlink)."
	@echo "  Source: $(CURDIR)/$(SRC_DIR)"
	@echo "  Target: $(GIMP_PLUGIN_DIR)/$(PLUGIN_NAME)"
	@echo ""
	@echo "Restart GIMP to load plugin."

install: check
	@mkdir -p $(GIMP_PLUGIN_DIR)/$(PLUGIN_NAME)
	@cp $(SRC_DIR)/* $(GIMP_PLUGIN_DIR)/$(PLUGIN_NAME)/
	@chmod +x $(GIMP_PLUGIN_DIR)/$(PLUGIN_NAME)/$(PLUGIN_NAME).py
	@echo "Install complete (copy)."
	@echo "  Target: $(GIMP_PLUGIN_DIR)/$(PLUGIN_NAME)"
	@echo ""
	@echo "Restart GIMP to load plugin."

uninstall:
	@if test -n "$(GIMP_CONFIG)"; then \
		rm -rf $(GIMP_PLUGIN_DIR)/$(PLUGIN_NAME); \
		echo "Plugin removed from $(GIMP_PLUGIN_DIR)."; \
	else \
		echo "GIMP 3.x config not found. Nothing to uninstall."; \
	fi

clean: uninstall
