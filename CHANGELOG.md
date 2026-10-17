# Changelog

## v2.0 — 2026-10-17

### Fixed
- **Shortcuts for apps that are not installed**: menu entries are created only for Adobe apps actually present in the Wine prefix (checked via the app's `.exe`); stale entries are removed.
- **Duplicate / extra menu entries**: wine-generated and leftover duplicates are cleaned up, leaving exactly one entry per app.
- **"Repair Icons & Shortcuts" could overwrite unrelated `.desktop` files** that merely contained a similar app name (e.g. `wine-extension-*.desktop` file associations, whose names include strings like "Substance 3D Designer Document"). It now only touches its own entries and duplicate shortcuts inside `wine/Programs`.
- **False "critical missing" warnings**: startup/diagnostics no longer flag shortcuts of apps you did not install (no more repair prompts on partial installs).
- **Wine leftovers after closing apps**: launching goes through a wrapper (`adobe-wine-run`) that runs the cleanup helper (`adobe-wine-kill`) when the app exits — helper processes (crashpad, Adobe Desktop Service, …) are stopped and the prefix is closed with `wineserver -k` when no other Wine app is running. Removes a common freeze/hang source on NVIDIA + KDE. Log: `~/.local/share/adobe-wine/cleanup.log`.
- **Wayland**: on Wayland sessions the panel makes sure Wine uses the `wayland` graphics driver (`HKCU\Software\Wine\Drivers` → `Graphics=wayland`) — the only fully working path for these apps.
- Hardcoded Turkish labels in diagnostics are now English (the UI itself stays TR/EN/DE).
- Uninstall also removes the generated launcher helpers.
- Version numbering aligned with GitHub releases (previous internal drafts were labelled v3.x; public releases are v1.0 → v2.0).

### Added
- Action **"Wine Cleanup"**: safe auto mode (helpers + close prefix if idle) with a follow-up option to force-close all Wine apps (`--full`).
- Action **"KDE/NVIDIA Window Fixes"**: sets "Prefer efficiency" color mode per display (fixes dark/stale windows on NVIDIA with KWin 6.8), allows tearing and adds a 99 % opacity window rule (KWin 6.8 dark-button workaround), with timestamped backups (`*.bak-YYYYMMDD-HHMMSS`) and a KWin reconfigure — no session restart needed.
- Launcher helpers in `~/.local/bin`: `adobe-wine-run` (launch + cleanup trap) and `adobe-wine-kill` (auto / `--helpers-only` / `--full`), regenerated automatically, old versions backed up.
- Diagnostics: Wayland graphics-driver row and KDE color-mode row (with guidance).
- README: troubleshooting section for dark windows, hangs on exit and X11 scaling.

## v1.0 — 2026-10-16
- Initial public release (previously internal v3.1/v3.2): trilingual PyQt6 panel (TR/EN/DE), patched Wine 11.19 manager (win32u Vulkan shared-resource fix, `d3dkmt_open_resource` fallback for `VK_KHR_external_memory_win32`), one-click runtimes (VCRedist, DirectX/DXVK/VKD3D, .NET, Python, Java, fonts), direct msvcp140/vcruntime DLL repair, Audition `winepulse` audio fix, Substance-style icons + start-menu integration, diagnostics with guided fixes.
