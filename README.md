# Adobe Substance 3D + Audition Wine Panel

A PyQt6 control panel to run **Adobe Substance 3D (Painter, Designer, Sampler)** and **Adobe Audition** on Linux via a **patched Wine build** (win32u Vulkan shared-resource fix), with one-click runtimes, DLL repair and start-menu integration.

Interface languages: **Türkçe / English / Deutsch** (switchable from the header, persisted in `~/.config/adobe-wine-panel/lang`).

![License](https://img.shields.io/badge/license-MIT-green) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![PyQt6](https://img.shields.io/badge/PyQt6-UI-purple) ![Arch](https://img.shields.io/badge/tested-Arch_Linux-black) ![Wine](https://img.shields.io/badge/wine-11.19_patched-red)

## Features

- **One-file app**: `adobe-wine-panel.py` — no install step, just run.
- **Patched Wine manager** (`/opt/wine-patched`, Wine 11.19):
  - Applies `d3dkmt_open_resource` fallback fix in `dlls/win32u/vulkan.c` for `VK_KHR_external_memory_win32`
  - Builds 32+64-bit with all CPU cores + `ccache`
  - Packages as `wine-patched` pacman package, wires `/usr/bin/wine*` symlinks, `wine.desktop` + MIME defaults
  - `pacman IgnorePkg` guard so updates can't break it
- **Adobe apps**:
  - Substance 3D Sampler, Designer, Painter + Audition 2026 launch cards
  - Generates official-style **Pt / Sa / Ds / Au** 256×256 PNG + SVG icons
  - Rebuilds KDE/GNOME start-menu `.desktop` entries, refreshes icon cache
- **Audio fix for Audition**: pins `HKCU\Software\Wine\Drivers\Audio` to `winepulse.drv` (PipeWire/PulseAudio)
- **Runtimes tab (one-click)**:
  - Visual C++ Redistributable 2005–2022 (x86 + x64)
  - Direct msvcp140/vcruntime140 DLL repair via `cabextract` (`vc_redist` → `system32`/`syswow64` + `wineserver -k` + `native,builtin` overrides)
  - DirectX 9/10/11/12, d3dcompiler, DXVK, VKD3D, Vulkan
  - Microsoft .NET Framework 4.8 + .NET Desktop Runtime 6.0 / 8.0 LTS
  - Windows Python 3.12 (amd64 + PIP) inside Wine
  - Eclipse Temurin Java JRE 21 LTS (Windows x64, MSI)
  - Corefonts, Tahoma, gdiplus, msxml3/6, winhttp, ucrtbase, webview2 stub
  - Winetricks GUI launcher
- **Diagnostics**: startup + on-demand scan (Wine core, icons, MIME, prefix, Vulkan, disk, runtimes) with guided fixes
- **Multilingual UI**: header language switcher (TR/EN/DE), auto-detects system locale on first run

## Requirements

- Arch Linux (or Arch-based; uses `pacman`, `makepkg`)
- Python 3.10+ with `PyQt6`
- Build deps (auto-installed): `base-devel`, `mingw-w64-gcc`, `ccache`, `winetricks`, `cabextract`, `unzip`, `p7zip`, `vulkan-headers`, etc.
- ~5 GB free space for Wine build + runtimes

## Quick start

```bash
git clone https://github.com/Utku92/adobe-substance-3d-audition-wine-panel.git
cd adobe-substance-3d-audition-wine-panel
pip install -r requirements.txt
chmod +x adobe-wine-panel.py
python3 adobe-wine-panel.py
```

1. Open **Apps & System → Check / Repair System** to build/install patched Wine.
2. Open **Runtimes → Install All Wine Runtimes in One Click** (5–15 min).
3. Install your Adobe apps into the default prefix (`~/.wine`) then launch them from the panel.

Custom prefix:

```bash
WINEPREFIX=~/wine-adobe python3 adobe-wine-panel.py
```

## Language

Click the language box in the header (`Türkçe / English / Deutsch`). Choice is saved to `~/.config/adobe-wine-panel/lang` and applied on next launch (the panel auto-restarts on change). First run auto-detects `LANG`/`LC_*`.

Desktop entries ship with `GenericName[tr/en/de]` and `Comment[tr/en/de]`.

## Project layout

```
adobe-substance-3d-audition-wine-panel/
├── adobe-wine-panel.py   # main app (TR/EN/DE, single file)
├── README.md
├── LICENSE              # MIT
├── requirements.txt
└── .gitignore
```

## Troubleshooting

- `Patched Wine not found` → run **Check / Repair System**.
- `msvcp140.dll missing` → **Direct DLL Repair** (tab 1 or Runtimes tab).
- No audio in Audition → **Audition Audio Backend Repair**, reopen Audition.
- Black 3D viewport → rebuild Wine (Vulkan patch), check `vulkaninfo`, install Vulkan drivers.
- Start-menu icons stale → **Repair Icons & Shortcuts**, or `kbuildsycoca6 --noincremental`.

## Disclaimer

Unofficial community tool. Not affiliated with Adobe Inc. or WineHQ. Adobe product names belong to their owners. You must own valid Adobe licenses. Patched Wine build is derived from WineHQ sources (LGPL-2.1-or-later).

## License

MIT — see [LICENSE](LICENSE).
