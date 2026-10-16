#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adobe Substance 3D + Audition · Wine Panel        (single file · v3.2)

This single file manages the "patched Wine" setup required to run Adobe
Substance 3D applications on Linux, official Substance 3D (Pt, Sa, Ds) app
icons, start-menu shortcuts, direct msvcp140 DLL repair and all Wine
runtimes (Visual C++ 2005-2022, .NET Framework/.NET 8, DirectX/DXVK/VKD3D,
Java, Python, Corefonts) in a tabbed interface.

License: MIT
"""
import os, sys, re, glob, shutil, subprocess

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QImage, QPainter, QColor, QFont, QPen
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QDialog, QPlainTextEdit, QMessageBox, QInputDialog,
    QTabWidget, QComboBox
)


# ------------------------------------------------------------------ dil / i18n (TR/EN/DE)
LANGS = ("tr", "en", "de")
LANG_NAMES = {"tr": "Türkçe", "en": "English", "de": "Deutsch"}
LANG_FILE = os.path.expanduser("~/.config/adobe-wine-panel/lang")

def _load_lang():
    try:
        v = open(LANG_FILE, encoding="utf-8").read().strip().lower()
        if v in LANGS:
            return v
    except Exception:
        pass
    # Default to English; user can switch via the header selector.
    # A saved choice in LANG_FILE always wins.
    return "en"

_LANG = _load_lang()

def get_lang():
    return _LANG

def set_lang(code):
    global _LANG
    if code not in LANGS:
        return False
    _LANG = code
    try:
        os.makedirs(os.path.dirname(LANG_FILE), exist_ok=True)
        with open(LANG_FILE, "w", encoding="utf-8") as f:
            f.write(code)
    except Exception:
        pass
    return True

TRANSLATIONS = {
    # genel
    "window_title": {"tr": "Adobe Substance 3D + Audition · Wine Panel", "en": "Adobe Substance 3D + Audition · Wine Panel", "de": "Adobe Substance 3D + Audition · Wine Panel"},
    "header_title": {"tr": "Adobe Substance 3D + Audition", "en": "Adobe Substance 3D + Audition", "de": "Adobe Substance 3D + Audition"},
    "header_sub": {"tr": "Wine Panel  ·  yamalı Wine, uygulama simgeleri, DLL onarımı ve tüm Windows gereksinimleri  ·  sürüm 3.2", "en": "Wine Panel  ·  patched Wine, app icons, DLL repair and all Windows runtimes  ·  v3.2", "de": "Wine Panel  ·  gepatchtes Wine, App-Icons, DLL-Reparatur und alle Windows-Laufzeiten  ·  v3.2"},
    "pill_checking": {"tr": "Sistem kontrol ediliyor…", "en": "Checking system…", "de": "System wird geprüft…"},
    "rtpill_checking": {"tr": "Gereksinimler kontrol ediliyor…", "en": "Checking runtimes…", "de": "Laufzeiten werden geprüft…"},
    "pill_ready": {"tr": "●  Wine Hazır  ·  {ok} kontrol tamam", "en": "●  Wine Ready  ·  {ok} checks passed", "de": "●  Wine bereit  ·  {ok} Prüfungen OK"},
    "pill_missing": {"tr": "●  {bad} kritik eksik var  ·  onarım gerekiyor", "en": "●  {bad} critical missing  ·  repair needed", "de": "●  {bad} kritisch fehlend  ·  Reparatur nötig"},
    "rtpill_done": {"tr": "📦  Gereksinimler: {d}/{t} kurulu", "en": "📦  Runtimes: {d}/{t} installed", "de": "📦  Laufzeiten: {d}/{t} installiert"},
    "rtpill_partial": {"tr": "📦  Gereksinimler: {d}/{t} kurulu (Sekmeden kurabilirsiniz)", "en": "📦  Runtimes: {d}/{t} installed (install from tab)", "de": "📦  Laufzeiten: {d}/{t} installiert (über Tab installieren)"},
    "tab_apps": {"tr": "🎨  Uygulamalar ve Sistem", "en": "🎨  Apps & System", "de": "🎨  Apps & System"},
    "tab_reqs": {"tr": "📦  Gereksinimler (VCRedist · DLL Fix · .NET · DirectX · Java · Python)", "en": "📦  Runtimes (VCRedist · DLL Fix · .NET · DirectX · Java · Python)", "de": "📦  Laufzeiten (VCRedist · DLL Fix · .NET · DirectX · Java · Python)"},
    "section_apps": {"tr": "ADOBE SUBSTANCE 3D + AUDITION UYGULAMALARI VE SİSTEM YÖNETİMİ", "en": "ADOBE SUBSTANCE 3D + AUDITION APPS & SYSTEM MANAGEMENT", "de": "ADOBE SUBSTANCE 3D + AUDITION APPS & SYSTEMVERWALTUNG"},
    "section_reqs": {"tr": "WINE ÇALIŞMA ZAMANI GEREKSİNİMLERİ (VCREDIST · DLL FIX · .NET · DIRECTX · JAVA · PYTHON)", "en": "WINE RUNTIME REQUIREMENTS (VCREDIST · DLL FIX · .NET · DIRECTX · JAVA · PYTHON)", "de": "WINE-LAUFZEITANFORDERUNGEN (VCREDIST · DLL FIX · .NET · DIRECTX · JAVA · PYTHON)"},
    "footer_install": {"tr": "Kurulum:", "en": "Install:", "de": "Installation:"},
    "footer_prefix": {"tr": "Wine öneki:", "en": "Wine prefix:", "de": "Wine-Präfix:"},
    "btn_about": {"tr": "Hakkında", "en": "About", "de": "Über"},
    "btn_close": {"tr": "Kapat", "en": "Close", "de": "Schließen"},
    "btn_yes": {"tr": "Evet", "en": "Yes", "de": "Ja"},
    "btn_no": {"tr": "Hayır", "en": "No", "de": "Nein"},
    "g_vulkan": {"tr": "Grafik sürücünüzün Vulkan desteğini ve Vulkan paketlerini kontrol edin; tanılama aracı yoksa vulkan-tools kurun.", "en": "Check your GPU driver Vulkan support and Vulkan packages; install vulkan-tools if the diagnostic tool is missing.", "de": "GPU-Treiber-Vulkan-Support und Vulkan-Pakete prüfen; vulkan-tools installieren falls das Diagnose-Tool fehlt."},
    "g_disk": {"tr": "Wine öneki ve Adobe kurulumları için diskte yer açın; 5 GB altındaki boş alan kurulumları aksatabilir.", "en": "Free up disk space for the Wine prefix and Adobe installs; less than 5 GB free can break setups.", "de": "Speicherplatz für Wine-Präfix und Adobe-Installationen freigeben; unter 5 GB frei kann Setups beschädigen."},
    "g_prefix": {"tr": "Seçili WINEPREFIX doğru mu kontrol edin. Önek eksikse önce Wine ile başlatın veya uygulamayı yeniden kurun.", "en": "Check that the selected WINEPREFIX is correct. If the prefix is missing, bootstrap it with Wine first or reinstall the app.", "de": "Prüfen, ob das gewählte WINEPREFIX korrekt ist. Falls das Präfix fehlt, zuerst mit Wine initialisieren oder App neu installieren."},
    "g_audio": {"tr": "Audition ses sorunlarında PipeWire/PulseAudio hizmetini ve paneldeki Audition ses onarımını kontrol edin.", "en": "For Audition audio issues, check the PipeWire/PulseAudio service and the panel Audition audio repair.", "de": "Bei Audition-Audioproblemen PipeWire-/PulseAudio-Dienst und Audition-Audio-Reparatur im Panel prüfen."},
    "g_rt": {"tr": "Eksik isteğe bağlı Windows bileşenlerini Gereksinimler sekmesinden kurun.", "en": "Install missing optional Windows components from the Runtimes tab.", "de": "Fehlende optionale Windows-Komponenten über den Laufzeiten-Tab installieren."},
    "g_crit": {"tr": "Kritik Wine veya panel yapılandırması eksik. Sistemi Denetle / Onar seçeneği ilgili onarım adımlarını sunar.", "en": "Critical Wine or panel configuration is missing. Check / Repair System offers the matching repair steps.", "de": "Kritische Wine- oder Panel-Konfiguration fehlt. System prüfen / reparieren bietet passende Reparaturschritte."},
    "g_short": {"tr": "Simgeleri ve Kısayolları Onar eylemiyle başlat menüsü kayıtlarını yenileyin.", "en": "Refresh start-menu entries with the Repair Icons & Shortcuts action.", "de": "Startmenü-Einträge mit Icons & Verknüpfungen reparieren aktualisieren."},
    "log_result_ok": {"tr": "başarılı", "en": "success", "de": "erfolgreich"},
    "log_result_fail": {"tr": "uyarı / hata kodu ({code})", "en": "warning / exit code ({code})", "de": "Warnung / Fehlercode ({code})"},
    "log_prefix": {"tr": "─── işlem sonucu: {res} ───", "en": "─── result: {res} ───", "de": "─── Ergebnis: {res} ───"},
    # kartlar sekme1
    "c_sampler_s": {"tr": "Materyal üretimi ve tarama", "en": "Material authoring & capture", "de": "Materialerstellung & Scan"},
    "c_sampler_d": {"tr": "Fotoğraflardan veya taranmış yüzeylerden PBR materyal üretir. 3D görünüm yamalı Wine ile render edilir.", "en": "Creates PBR materials from photos or scanned surfaces. 3D view renders via patched Wine.", "de": "Erstellt PBR-Materialien aus Fotos oder Scans. 3D-Ansicht rendert über gepatchtes Wine."},
    "c_designer_s": {"tr": "Düğüm tabanlı materyal yazarlığı", "en": "Node-based material authoring", "de": "Knotenbasiertes Material-Authoring"},
    "c_designer_d": {"tr": "Prosedürel materyalleri düğümlerle kurar ve dışa aktarır. 3D görünüm yamalı Wine ile render edilir.", "en": "Builds and exports procedural materials with nodes. 3D view renders via patched Wine.", "de": "Erstellt und exportiert prozedurale Materialien mit Knoten. 3D-Ansicht rendert über gepatchtes Wine."},
    "c_painter_s": {"tr": "3D yüzey boyama", "en": "3D surface painting", "de": "3D-Oberflächenbemalung"},
    "c_painter_d": {"tr": "3D modellerin üzerinde fırçalarla boyama yapar. DİKKAT: açılışta Adobe girişi gerektirir.", "en": "Paints directly on 3D models with brushes. NOTE: requires Adobe login on launch.", "de": "Bemalt 3D-Modelle direkt mit Pinseln. HINWEIS: Adobe-Login beim Start erforderlich."},
    "c_audition_s": {"tr": "Ses düzenleme ve miksaj", "en": "Audio editing & mixing", "de": "Audiobearbeitung & Mischung"},
    "c_audition_d": {"tr": "Çok izli ses düzenleme, miksaj ve mastering. winepulse (PipeWire/PulseAudio) ile çalışır.", "en": "Multitrack editing, mixing and mastering. Works via winepulse (PipeWire/PulseAudio).", "de": "Mehrspur-Schnitt, Mischung und Mastering. Läuft über winepulse (PipeWire/PulseAudio)."},
    "c_audiofix_t": {"tr": "Audition Ses Altyapısı Onarımı", "en": "Audition Audio Backend Repair", "de": "Audition-Audio-Backend-Reparatur"},
    "c_audiofix_s": {"tr": "winepulse backend + Audition kısayolu", "en": "winepulse backend + Audition shortcut", "de": "winepulse-Backend + Audition-Verknüpfung"},
    "c_audiofix_d": {"tr": "Ses sürücüsünü winepulse.drv'ye sabitler, Audition başlat menüsü kısayolunu ve simgesini üretir.", "en": "Pins audio driver to winepulse.drv, rebuilds Audition start-menu shortcut and icon.", "de": "Fixiert Audiotreiber auf winepulse.drv, erstellt Audition-Startmenü-Link und Icon neu."},
    "c_dllfix_t": {"tr": "msvcp140.dll (VC++ x64) Doğrudan DLL Onarımı", "en": "msvcp140.dll (VC++ x64) Direct DLL Repair", "de": "msvcp140.dll (VC++ x64) Direkt-DLL-Reparatur"},
    "c_dllfix_s": {"tr": "cabextract vc_redist.x64.exe -> system32/msvcp140*.dll + wineserver -k", "en": "cabextract vc_redist.x64.exe -> system32/msvcp140*.dll + wineserver -k", "de": "cabextract vc_redist.x64.exe -> system32/msvcp140*.dll + wineserver -k"},
    "c_dllfix_d": {"tr": "vc_redist.x64.exe içinden msvcp140, _1, _2, _atomic_wait ve _codecvt_ids DLL'lerini ayıklayıp doğrudan system32'ye yazar.", "en": "Extracts msvcp140, _1, _2, _atomic_wait and _codecvt_ids DLLs from vc_redist.x64.exe directly into system32.", "de": "Extrahiert msvcp140, _1, _2, _atomic_wait und _codecvt_ids aus vc_redist.x64.exe direkt nach system32."},
    "c_shortcuts_t": {"tr": "Simgeleri ve Kısayolları Onar", "en": "Repair Icons & Shortcuts", "de": "Icons & Verknüpfungen reparieren"},
    "c_shortcuts_s": {"tr": "Orijinal Pt, Sa, Ds simgeleri · KDE önbellek yenileme", "en": "Original Pt, Sa, Ds icons · KDE cache refresh", "de": "Originale Pt-, Sa-, Ds-Icons · KDE-Cache-Aktualisierung"},
    "c_shortcuts_d": {"tr": "Resmi Substance 3D (Pt, Sa, Ds) simgelerini 256x256 PNG olarak üretir ve KDE Başlat Menüsünü anında yeniler.", "en": "Generates official Substance 3D (Pt, Sa, Ds) icons as 256x256 PNG and refreshes the KDE start menu instantly.", "de": "Erzeugt offizielle Substance-3D-Icons (Pt, Sa, Ds) als 256x256 PNG und aktualisiert das KDE-Startmenü sofort."},
    "c_winecfg_t": {"tr": "Wine Ayarları (winecfg)", "en": "Wine Settings (winecfg)", "de": "Wine-Einstellungen (winecfg)"},
    "c_winecfg_s": {"tr": "Windows sürümü ve grafik yapılandırması", "en": "Windows version & graphics config", "de": "Windows-Version & Grafikkonfiguration"},
    "c_winecfg_d": {"tr": "Windows sürümü, sürücü eşlemeleri, ekran DPI ve ses/grafik ayarlarını düzenler.", "en": "Edits Windows version, drive mappings, screen DPI and audio/graphics settings.", "de": "Bearbeitet Windows-Version, Laufwerkszuordnungen, Bildschirm-DPI und Audio-/Grafikeinstellungen."},
    "c_diagnose_t": {"tr": "Otomatik Sorun Tespiti", "en": "Automatic Diagnostics", "de": "Automatische Diagnose"},
    "c_diagnose_s": {"tr": "Wine, Adobe, ses ve gereksinimleri tara", "en": "Scan Wine, Adobe, audio & runtimes", "de": "Wine, Adobe, Audio & Laufzeiten prüfen"},
    "c_diagnose_d": {"tr": "Sistem açılışında otomatik taranır. Bu düğmeyle kontrolleri istediğiniz zaman yeniden çalıştırıp bulunan eksikleri ve önerileri görebilirsiniz.", "en": "Auto-scans on startup. Re-run checks anytime to see missing items and suggestions.", "de": "Automatischer Scan beim Start. Prüfungen jederzeit erneut ausführen, um Fehlendes und Vorschläge zu sehen."},
    "c_check_t": {"tr": "Sistemi Denetle / Onar", "en": "Check / Repair System", "de": "System prüfen / reparieren"},
    "c_check_s": {"tr": "Altyapı kontrolü · sıfırdan kurulum", "en": "Infrastructure check · fresh install", "de": "Infrastrukturprüfung · Neuinstallation"},
    "c_check_d": {"tr": "Eksikleri bulur; kısayol/MIME eksiklerini anında onarır, Wine eksikse ccache ile hızla derleyerek kurar.", "en": "Finds gaps; instantly repairs shortcut/MIME issues, rebuilds Wine fast with ccache if missing.", "de": "Findet Lücken; repariert Shortcut-/MIME-Probleme sofort, baut Wine bei Bedarf schnell mit ccache."},
    "c_updates_t": {"tr": "Güncellemeyi Denetle", "en": "Check for Updates", "de": "Updates prüfen"},
    "c_updates_s": {"tr": "upstream ile karşılaştırma", "en": "compare with upstream", "de": "Abgleich mit Upstream"},
    "c_updates_d": {"tr": "Kurulu Wine sürümünü dl.winehq.org üzerindeki sürümlerle karşılaştırır.", "en": "Compares installed Wine version against releases on dl.winehq.org.", "de": "Vergleicht installierte Wine-Version mit Releases auf dl.winehq.org."},
    "c_rebuild_t": {"tr": "Yeniden Derle (ccache hızlandırmalı)", "en": "Rebuild (ccache accelerated)", "de": "Neu bauen (ccache-beschleunigt)"},
    "c_rebuild_s": {"tr": "32+64 bit · tüm CPU çekirdekleri + ccache", "en": "32+64 bit · all CPU cores + ccache", "de": "32+64 Bit · alle CPU-Kerne + ccache"},
    "c_rebuild_d": {"tr": "Yamalı Wine'ı ccache önbelleğiyle baştan derleyip kurar. Yeni Wine sürümüne geçmek için kullanın.", "en": "Rebuilds and reinstalls patched Wine from scratch with ccache. Use to move to a new Wine version.", "de": "Baut gepatchtes Wine mit ccache von Grund auf neu. Für Wechsel auf neue Wine-Version."},
    "c_guard_t": {"tr": "Korumayı Uygula", "en": "Apply Protection", "de": "Schutz anwenden"},
    "c_guard_s": {"tr": "pacman IgnorePkg · güncelleme dokunmasın", "en": "pacman IgnorePkg · block updates", "de": "pacman IgnorePkg · Updates blockieren"},
    "c_guard_d": {"tr": "Yamalı Wine'ı ve derleme araçlarını pacman güncellemelerinden korur. Bozulmayı baştan engeller.", "en": "Protects patched Wine and build tools from pacman updates. Prevents breakage upfront.", "de": "Schützt gepatchtes Wine und Build-Tools vor pacman-Updates. Verhindert Beschädigung im Voraus."},
    "c_uninstall_t": {"tr": "Kaldır", "en": "Uninstall", "de": "Deinstallieren"},
    "c_uninstall_s": {"tr": "tam temizlik", "en": "full cleanup", "de": "vollständige Bereinigung"},
    "c_uninstall_d": {"tr": "Yamalı Wine paketini, kurulum dizinini, özel simgeleri ve tüm masaüstü/MIME kayıtlarını siler.", "en": "Removes patched Wine package, install dir, custom icons and all desktop/MIME entries.", "de": "Entfernt gepatchtes Wine-Paket, Installationsordner, eigene Icons und alle Desktop-/MIME-Einträge."},
    # kartlar sekme2
    "r_all_t": {"tr": "Tüm Wine Gereksinimlerini Tek Tıkla Kur (Önerilen)", "en": "Install All Wine Runtimes in One Click (Recommended)", "de": "Alle Wine-Laufzeiten mit einem Klick installieren (empfohlen)"},
    "r_all_s": {"tr": "All-in-One: VCRedist 2005-2022 + msvcp140 DLL Fix + DirectX/DXVK/VKD3D + .NET + Python + Java + Yazı Tipleri", "en": "All-in-One: VCRedist 2005-2022 + msvcp140 DLL Fix + DirectX/DXVK/VKD3D + .NET + Python + Java + Fonts", "de": "All-in-One: VCRedist 2005-2022 + msvcp140 DLL-Fix + DirectX/DXVK/VKD3D + .NET + Python + Java + Schriften"},
    "r_all_d": {"tr": "Adobe Substance 3D, Audition ve diğer tüm Windows uygulamalarının sorunsuz çalışması için gereken bütün kütüphaneleri sırayla kurar.", "en": "Installs all libraries needed for Adobe Substance 3D, Audition and other Windows apps to run smoothly.", "de": "Installiert alle Bibliotheken für Adobe Substance 3D, Audition und andere Windows-Apps."},
    "r_dllfix_s": {"tr": "msvcp140 · msvcp140_1 · msvcp140_2 · msvcp140_atomic_wait · msvcp140_codecvt_ids", "en": "msvcp140 · msvcp140_1 · msvcp140_2 · msvcp140_atomic_wait · msvcp140_codecvt_ids", "de": "msvcp140 · msvcp140_1 · msvcp140_2 · msvcp140_atomic_wait · msvcp140_codecvt_ids"},
    "r_dllfix_d": {"tr": "vc_redist.x64.exe paketini cabextract ile /tmp/vc64/out dizinine açar, 64-bit msvcp140 DLL'lerini system32'ye kopyalar ve wineserver'ı yeniden başlatır.", "en": "Extracts vc_redist.x64.exe via cabextract to /tmp/vc64/out, copies 64-bit msvcp140 DLLs to system32 and restarts wineserver.", "de": "Entpackt vc_redist.x64.exe per cabextract nach /tmp/vc64/out, kopiert 64-Bit-msvcp140-DLLs nach system32 und startet wineserver neu."},
    "r_vc_t": {"tr": "Tüm Visual C++ Redistributable Paketleri (2005–2022)", "en": "All Visual C++ Redistributable Packages (2005–2022)", "de": "Alle Visual C++ Redistributable-Pakete (2005–2022)"},
    "r_vc_s": {"tr": "vcrun2005 · vcrun2008 · vcrun2010 · vcrun2012 · vcrun2013 · vcrun2022 (x86 & x64) + DLL Fix", "en": "vcrun2005 · vcrun2008 · vcrun2010 · vcrun2012 · vcrun2013 · vcrun2022 (x86 & x64) + DLL Fix", "de": "vcrun2005 · vcrun2008 · vcrun2010 · vcrun2012 · vcrun2013 · vcrun2022 (x86 & x64) + DLL-Fix"},
    "r_vc_d": {"tr": "Eksik msvcp140.dll, vcruntime140.dll, mfc140u.dll ve eski C++ çalışma zamanı hatalarının tamamını çözer.", "en": "Fixes all missing msvcp140.dll, vcruntime140.dll, mfc140u.dll and legacy C++ runtime errors.", "de": "Behebt alle fehlenden msvcp140.dll, vcruntime140.dll, mfc140u.dll und ältere C++-Laufzeitfehler."},
    "r_dx_t": {"tr": "DirectX 9/10/11/12, DXVK, VKD3D ve HLSL Derleyicileri", "en": "DirectX 9/10/11/12, DXVK, VKD3D & HLSL Compilers", "de": "DirectX 9/10/11/12, DXVK, VKD3D & HLSL-Compiler"},
    "r_dx_s": {"tr": "d3dx9 · d3dcompiler_43 · d3dcompiler_47 · dxvk · vkd3d · vulkan", "en": "d3dx9 · d3dcompiler_43 · d3dcompiler_47 · dxvk · vkd3d · vulkan", "de": "d3dx9 · d3dcompiler_43 · d3dcompiler_47 · dxvk · vkd3d · vulkan"},
    "r_dx_d": {"tr": "DirectX çağrılarını Vulkan'a çevirir, Adobe Substance 3D ve oyunlarda shader derleme hatalarını giderir.", "en": "Translates DirectX calls to Vulkan, fixes shader compile errors in Adobe Substance 3D and games.", "de": "Übersetzt DirectX-Aufrufe nach Vulkan, behebt Shader-Compiler-Fehler in Adobe Substance 3D und Spielen."},
    "r_dot_t": {"tr": "Microsoft .NET Framework 4.8 & .NET Desktop Runtime (6.0 / 8.0)", "en": "Microsoft .NET Framework 4.8 & .NET Desktop Runtime (6.0 / 8.0)", "de": "Microsoft .NET Framework 4.8 & .NET Desktop Runtime (6.0 / 8.0)"},
    "r_dot_s": {"tr": "dotnet48 + Microsoft WindowsDesktop Runtime 6.0 LTS & 8.0 LTS (x64)", "en": "dotnet48 + Microsoft WindowsDesktop Runtime 6.0 LTS & 8.0 LTS (x64)", "de": "dotnet48 + Microsoft WindowsDesktop Runtime 6.0 LTS & 8.0 LTS (x64)"},
    "r_dot_d": {"tr": "Hem klasik .NET Framework 4.8 hem de modern .NET 6/8 tabanlı Windows arayüz ve araçlarının çalışmasını sağlar.", "en": "Enables both classic .NET Framework 4.8 and modern .NET 6/8 based Windows UI and tools.", "de": "Ermöglicht klassisches .NET Framework 4.8 sowie moderne .NET-6/8-basierte Windows-UI und Tools."},
    "r_py_t": {"tr": "Python 3.12 (Windows 64-bit Yerel Kurulum + PIP)", "en": "Python 3.12 (Windows 64-bit Native + PIP)", "de": "Python 3.12 (Windows 64-Bit nativ + PIP)"},
    "r_py_s": {"tr": "Wine içine resmi Windows Python 3.12.8 (amd64) kurar ve PATH'e ekler", "en": "Installs official Windows Python 3.12.8 (amd64) into Wine and adds to PATH", "de": "Installiert offizielles Windows-Python 3.12.8 (amd64) in Wine und fügt es zu PATH hinzu"},
    "r_py_d": {"tr": "Adobe Substance 3D eklentileri, betikleri ve Windows tabanlı Python araçları için Wine içinde çalışan Python ortamı.", "en": "Python environment inside Wine for Adobe Substance 3D plugins, scripts and Windows Python tools.", "de": "Python-Umgebung in Wine für Adobe-Substance-3D-Plugins, Skripte und Windows-Python-Tools."},
    "r_java_t": {"tr": "Java Runtime Environment (Eclipse Temurin JRE 21 LTS 64-bit)", "en": "Java Runtime Environment (Eclipse Temurin JRE 21 LTS 64-bit)", "de": "Java Runtime Environment (Eclipse Temurin JRE 21 LTS 64-Bit)"},
    "r_java_s": {"tr": "Wine içine Windows JRE 21 LTS (.msi) kurar ve JAVA_HOME/PATH ayarlar", "en": "Installs Windows JRE 21 LTS (.msi) into Wine and sets JAVA_HOME/PATH", "de": "Installiert Windows-JRE 21 LTS (.msi) in Wine und setzt JAVA_HOME/PATH"},
    "r_java_d": {"tr": "Java tabanlı Windows uygulamaları ve araçları için Wine önekine tam uyumlu 64-bit Java desteği ekler.", "en": "Adds fully compatible 64-bit Java support to the Wine prefix for Java-based Windows apps.", "de": "Fügt voll kompatible 64-Bit-Java-Unterstützung zum Wine-Präfix für Java-basierte Windows-Apps hinzu."},
    "r_fonts_t": {"tr": "Temel Windows Yazı Tipleri ve Sistem DLL Bileşenleri", "en": "Core Windows Fonts & System DLL Components", "de": "Kern-Windows-Schriften & System-DLL-Komponenten"},
    "r_fonts_s": {"tr": "corefonts · tahoma · gdiplus · msxml3 · msxml6 · winhttp · ucrtbase · webview2", "en": "corefonts · tahoma · gdiplus · msxml3 · msxml6 · winhttp · ucrtbase · webview2", "de": "corefonts · tahoma · gdiplus · msxml3 · msxml6 · winhttp · ucrtbase · webview2"},
    "r_fonts_d": {"tr": "Adobe kurucularında ve uygulama pencerelerinde boş/bozuk yazı tipi veya XML/HTTP bağlantı hatalarını önler.", "en": "Prevents empty/broken fonts or XML/HTTP connection errors in Adobe installers and app windows.", "de": "Verhindert leere/defekte Schriften oder XML-/HTTP-Verbindungsfehler in Adobe-Installern und App-Fenstern."},
    "r_wt_t": {"tr": "Winetricks Grafik Arayüzünü Aç", "en": "Open Winetricks GUI", "de": "Winetricks-GUI öffnen"},
    "r_wt_s": {"tr": "Özel DLL / bileşen yönetimi · regedit · wineconsole", "en": "Custom DLL / component management · regedit · wineconsole", "de": "Benutzerdefinierte DLL-/Komponentenverwaltung · regedit · wineconsole"},
    "r_wt_d": {"tr": "Winetricks penceresini yamalı Wine ile açarak yüzlerce ek Windows bileşenini elle yönetmenizi sağlar.", "en": "Opens the Winetricks window with patched Wine to manually manage hundreds of extra Windows components.", "de": "Öffnet das Winetricks-Fenster mit gepatchtem Wine zur manuellen Verwaltung hunderter Windows-Komponenten."},
    # diyaloglar
    "d_wine_missing_t": {"tr": "Yamalı Wine bulunamadı", "en": "Patched Wine not found", "de": "Gepatchtes Wine nicht gefunden"},
    "d_wine_missing_b": {"tr": "Önce 1. sekmedeki <b>Sistemi Denetle / Onar</b> seçeneğini çalıştırın.", "en": "First run <b>Check / Repair System</b> in tab 1.", "de": "Führen Sie zuerst <b>System prüfen / reparieren</b> in Tab 1 aus."},
    "d_notfound_b": {"tr": "Önce Adobe uygulamasını bu Wine önekine kurun.", "en": "Install the Adobe app into this Wine prefix first.", "de": "Installieren Sie zuerst die Adobe-App in dieses Wine-Präfix."},
    "d_notfound_suf": {"tr": "kurulu değil", "en": "is not installed", "de": "ist nicht installiert"},
    "d_started_suf": {"tr": "başlatıldı", "en": "launched", "de": "gestartet"},
    "d_started_b": {"tr": "Uygulama açılıyor.<br><br>3D görünüm, yamalı Wine sayesinde render edilir.", "en": "Launching app.<br><br>3D view renders thanks to patched Wine.", "de": "App wird gestartet.<br><br>3D-Ansicht rendert dank gepatchtem Wine."},
    "d_error_t": {"tr": "Hata", "en": "Error", "de": "Fehler"},
    "d_audio_done": {"tr": "Audition Ses Onarımı Tamam", "en": "Audition Audio Repair Done", "de": "Audition-Audio-Reparatur fertig"},
    "d_audio_check": {"tr": "Audition Ses Onarımı (Kontrol Et)", "en": "Audition Audio Repair (Check)", "de": "Audition-Audio-Reparatur (prüfen)"},
    "d_audio_b": {"tr": "Ses backend <b>winepulse.drv</b> (PipeWire/PulseAudio) olarak ayarlandı.", "en": "Audio backend set to <b>winepulse.drv</b> (PipeWire/PulseAudio).", "de": "Audio-Backend auf <b>winepulse.drv</b> (PipeWire/PulseAudio) gesetzt."},
    "d_audio_reopen": {"tr": "Audition açıksa kapatıp yeniden açın.", "en": "If Audition is open, close and reopen it.", "de": "Falls Audition offen ist, schließen und neu öffnen."},
    "d_audio_err": {"tr": "Ses onarımı sırasında hata:", "en": "Error during audio repair:", "de": "Fehler bei Audio-Reparatur:"},
    "d_rtall_t": {"tr": "Tüm Wine Gereksinimlerini Kur", "en": "Install All Wine Runtimes", "de": "Alle Wine-Laufzeiten installieren"},
    "d_rtall_q": {"tr": "Aşağıdaki tüm paketler <b>{prefix}</b> önekine sırayla kurulacak:<br><br>• <b>Visual C++ Redistributable</b> (2005–2022 x86/x64)<br>• <b>msvcp140*.dll Doğrudan Onarımı</b><br>• <b>DirectX 9/10/11/12</b> (DXVK, VKD3D)<br>• <b>Microsoft .NET</b> (6.0 & 8.0 LTS + 4.8)<br>• <b>Python 3.12</b> + <b>Java JRE 21 LTS</b><br>• <b>Yazı Tipleri & Sistem DLL</b><br><br>5–15 dakika sürebilir. Başlatılsın mı?", "en": "All packages below will be installed into <b>{prefix}</b> in order:<br><br>• <b>Visual C++ Redistributable</b> (2005–2022 x86/x64)<br>• <b>msvcp140*.dll Direct Repair</b><br>• <b>DirectX 9/10/11/12</b> (DXVK, VKD3D)<br>• <b>Microsoft .NET</b> (6.0 & 8.0 LTS + 4.8)<br>• <b>Python 3.12</b> + <b>Java JRE 21 LTS</b><br>• <b>Fonts & System DLLs</b><br><br>May take 5–15 min. Start now?", "de": "Alle Pakete werden der Reihe nach in <b>{prefix}</b> installiert:<br><br>• <b>Visual C++ Redistributable</b> (2005–2022 x86/x64)<br>• <b>msvcp140*.dll Direkt-Reparatur</b><br>• <b>DirectX 9/10/11/12</b> (DXVK, VKD3D)<br>• <b>Microsoft .NET</b> (6.0 & 8.0 LTS + 4.8)<br>• <b>Python 3.12</b> + <b>Java JRE 21 LTS</b><br>• <b>Schriften & System-DLLs</b><br><br>Dauert 5–15 Min. Jetzt starten?"},
    "d_shortcuts_t": {"tr": "Simgeler ve Kısayollar Onarıldı", "en": "Icons & Shortcuts Repaired", "de": "Icons & Verknüpfungen repariert"},
    "d_shortcuts_q": {"tr": "KDE Başlat Menüsü simge önbelleğinin anında yenilenmesi için masaüstü paneli şimdi yeniden başlatılsın mı? (1-2 saniye sürer, açık uygulamalar kapanmaz)", "en": "Restart the desktop panel now to instantly refresh the KDE start-menu icon cache? (takes 1-2s, open apps stay open)", "de": "Desktop-Panel jetzt neu starten, um KDE-Icon-Cache sofort zu aktualisieren? (dauert 1–2 s, offene Apps bleiben offen)"},
    "d_shortcuts_gen": {"tr": "Resmi Substance 3D (<b>Pt, Sa, Ds</b>) simgeleri üretildi:", "en": "Official Substance 3D (<b>Pt, Sa, Ds</b>) icons generated:", "de": "Offizielle Substance-3D-Icons (<b>Pt, Sa, Ds</b>) erzeugt:"},
    "d_shortcuts_err": {"tr": "Kısayollar onarılırken hata oluştu:", "en": "Error while repairing shortcuts:", "de": "Fehler beim Reparieren der Verknüpfungen:"},
    "d_check_ok_t": {"tr": "Sistem hazır", "en": "System ready", "de": "System bereit"},
    "d_check_ok_b": {"tr": "Tüm kritik Wine, simge ve başlat menüsü kontrolleri tamam.", "en": "All critical Wine, icon and start-menu checks passed.", "de": "Alle kritischen Wine-, Icon- und Startmenü-Prüfungen bestanden."},
    "d_cfg_missing_t": {"tr": "Yapılandırma eksikleri var", "en": "Configuration gaps found", "de": "Konfigurationslücken gefunden"},
    "d_cfg_missing_q": {"tr": "Derleme yapmadan hemen şimdi hızlıca onarılsın mı?", "en": "Repair quickly now without rebuilding?", "de": "Jetzt schnell ohne Neubau reparieren?"},
    "d_cfg_build_ok": {"tr": "Wine derlemesi sağlam ancak <b>{bad} yapılandırma maddesi</b> eksik:", "en": "Wine build is fine but <b>{bad} config items</b> are missing:", "de": "Wine-Build ist OK, aber <b>{bad} Konfigurationseinträge</b> fehlen:"},
    "d_missing_t": {"tr": "Eksikler var", "en": "Missing items", "de": "Fehlende Einträge"},
    "d_missing_q": {"tr": "Şimdi onarılsın mı? (Yamalı Wine baştan indirilir ve derlenir).", "en": "Repair now? (Patched Wine will be downloaded and built).", "de": "Jetzt reparieren? (Gepatchtes Wine wird geladen und gebaut)."},
    "d_missing_n": {"tr": "<b>{bad} kritik madde</b> eksik:", "en": "<b>{bad} critical items</b> missing:", "de": "<b>{bad} kritische Einträge</b> fehlen:"},
    "d_diag_fail_t": {"tr": "Sorun taraması tamamlanamadı", "en": "Diagnostics failed", "de": "Diagnose fehlgeschlagen"},
    "d_diag_fail_b": {"tr": "Kontroller çalışırken hata oluştu:", "en": "Error while running checks:", "de": "Fehler beim Ausführen der Prüfungen:"},
    "d_diag_t": {"tr": "Otomatik sorun tespiti", "en": "Automatic diagnostics", "de": "Automatische Diagnose"},
    "d_diag_b": {"tr": "Tarama tamamlandı: <b>{ok} kontrol uygun</b>, <b>{bad} kritik sorun</b>, <b>{n} uyarı/eksik</b>.", "en": "Scan complete: <b>{ok} OK</b>, <b>{bad} critical</b>, <b>{n} warnings/missing</b>.", "de": "Scan abgeschlossen: <b>{ok} OK</b>, <b>{bad} kritisch</b>, <b>{n} Warnungen/fehlend</b>."},
    "d_diag_steps": {"tr": "<b>Önerilen adımlar:</b>", "en": "<b>Suggested steps:</b>", "de": "<b>Empfohlene Schritte:</b>"},
    "d_diag_none": {"tr": "Kritik sorun bulunmadı. Uygulama bazındaki isteğe bağlı kontrolleri aşağıdan inceleyin.", "en": "No critical issues. See optional per-app checks below.", "de": "Keine kritischen Probleme. Optionale App-Prüfungen unten ansehen."},
    "d_rebuild_t": {"tr": "Yeniden derle", "en": "Rebuild", "de": "Neu bauen"},
    "d_rebuild_b": {"tr": "Yamalı Wine <b>ccache hızlandırmasıyla baştan derlenip kurulacak</b>.<br><br>Devam edilsin mi?", "en": "Patched Wine will be <b>rebuilt from scratch with ccache</b>.<br><br>Continue?", "de": "Gepatchtes Wine wird <b>mit ccache von Grund auf neu gebaut</b>.<br><br>Fortfahren?"},
    "d_guard_ok_t": {"tr": "Koruma etkin", "en": "Protection active", "de": "Schutz aktiv"},
    "d_guard_ok_b": {"tr": "Aşağıdaki paketlere <b>pacman güncelleme yapamaz</b>:", "en": "Pacman <b>cannot update</b> these packages:", "de": "Pacman <b>kann</b> diese Pakete <b>nicht aktualisieren</b>:"},
    "d_guard_ok_f": {"tr": "Böylece bir sistem güncellemesi kurulumu bozamaz.", "en": "So a system update cannot break the install.", "de": "So kann ein Systemupdate die Installation nicht beschädigen."},
    "d_guard_fail_t": {"tr": "Koruma uygulanamadı", "en": "Protection failed", "de": "Schutz fehlgeschlagen"},
    "d_guard_fail_b": {"tr": "<tt>/etc/pacman.conf</tt> yazılamadı.<br>Yönetici yetkisiyle çalıştırmayı deneyin.", "en": "Could not write <tt>/etc/pacman.conf</tt>.<br>Try running with admin rights.", "de": "<tt>/etc/pacman.conf</tt> konnte nicht geschrieben werden.<br>Mit Adminrechten versuchen."},
    "d_uninstall_t": {"tr": "Yamalı Wine kaldırılsın mı?", "en": "Remove patched Wine?", "de": "Gepatchtes Wine entfernen?"},
    "d_uninstall_word": {"tr": "SİL", "en": "DELETE", "de": "LÖSCHEN"},
    "d_uninstall_b": {"tr": "Bu işlem <b>geri alınamaz</b>.<br><br>• <b>wine-patched</b> paketi silinir<br>• <b>/opt/wine-patched</b> dizini silinir<br>• masaüstü, simge ve MIME kayıtları temizlenir<br><br><b>Adobe uygulamaları silinmez</b>, ama Wine olmadan açılmazlar.", "en": "This cannot be <b>undone</b>.<br><br>• <b>wine-patched</b> package removed<br>• <b>/opt/wine-patched</b> deleted<br>• desktop, icon and MIME entries cleaned<br><br><b>Adobe apps are kept</b>, but won't launch without Wine.", "de": "Dies kann <b>nicht rückgängig</b> gemacht werden.<br><br>• <b>wine-patched</b>-Paket entfernt<br>• <b>/opt/wine-patched</b> gelöscht<br>• Desktop-, Icon- und MIME-Einträge bereinigt<br><br><b>Adobe-Apps bleiben</b>, starten aber ohne Wine nicht."},
    "d_uninstall_confirm": {"tr": "Onaylamak için <b>{w}</b> yazın:", "en": "Type <b>{w}</b> to confirm:", "de": "Zum Bestätigen <b>{w}</b> eingeben:"},
    "d_about_b": {"tr": "<b>Sürüm 3.2</b> · MIT · 3 dil (TR/EN/DE)<br><br>Bu panel, Adobe Substance 3D + Audition uygulamalarını Linux'ta çalıştırmak için gerekli <b>özel derlenmiş Wine</b> kurulumunu, resmi <b>Pt / Sa / Ds</b> uygulama simgelerini, <b>msvcp140 doğrudan DLL onarımını</b> ve <b>VCRedist, .NET, DirectX/DXVK, Java, Python</b> gereksinimlerini yönetir.", "en": "<b>v3.2</b> · MIT · 3 languages (TR/EN/DE)<br><br>This panel manages the <b>custom Wine build</b> needed to run Adobe Substance 3D + Audition on Linux, official <b>Pt / Sa / Ds</b> icons, <b>direct msvcp140 DLL repair</b> and <b>VCRedist, .NET, DirectX/DXVK, Java, Python</b> runtimes.", "de": "<b>v3.2</b> · MIT · 3 Sprachen (TR/EN/DE)<br><br>Dieses Panel verwaltet den <b>angepassten Wine-Build</b> für Adobe Substance 3D + Audition unter Linux, offizielle <b>Pt-/Sa-/Ds</b>-Icons, <b>direkte msvcp140-DLL-Reparatur</b> und <b>VCRedist-, .NET-, DirectX/DXVK-, Java-, Python</b>-Laufzeiten."},
    "d_startup_t": {"tr": "Wine kurulumu eksik veya bozulmuş görünüyor", "en": "Wine install looks missing or broken", "de": "Wine-Installation scheint zu fehlen oder defekt"},
    "d_startup_b": {"tr": "Bir güncelleme ya da eksik kurulum buna sebep olmuş olabilir.<br><br>Şimdi kontrol edilip onarılsın mı?", "en": "An update or incomplete install may have caused this.<br><br>Check and repair now?", "de": "Ein Update oder eine unvollständige Installation kann die Ursache sein.<br><br>Jetzt prüfen und reparieren?"},
    "d_startup_n": {"tr": "<b>{bad} kritik madde</b> eksik.", "en": "<b>{bad} critical items</b> missing.", "de": "<b>{bad} kritische Einträge</b> fehlen."},
    "d_lang_restart_t": {"tr": "Dil değiştirildi", "en": "Language changed", "de": "Sprache geändert"},
    "d_lang_restart_b": {"tr": "Arayüz dili güncellendi. Değişikliğin tam uygulanması için panel yeniden başlatılacak.", "en": "UI language updated. The panel will restart to apply it fully.", "de": "UI-Sprache aktualisiert. Das Panel wird neu gestartet, um sie vollständig zu übernehmen."},
    "t_quick_repair": {"tr": "Hızlı Yapılandırma Onarımı", "en": "Quick Config Repair", "de": "Schnelle Konfigurationsreparatur"},
    "t_sys_repair": {"tr": "Sistem Onarımı", "en": "System Repair", "de": "Systemreparatur"},
    "t_all_rt": {"tr": "Tüm Wine Gereksinimleri Kurulumu", "en": "Install All Wine Runtimes", "de": "Alle Wine-Laufzeiten installieren"},
    "t_dllfix": {"tr": "msvcp140.dll (VC++ x64) Doğrudan DLL Onarımı", "en": "msvcp140.dll (VC++ x64) Direct DLL Repair", "de": "msvcp140.dll (VC++ x64) Direkt-DLL-Reparatur"},
    "t_vc": {"tr": "Visual C++ (2005–2022) Kurulumu", "en": "Visual C++ (2005–2022) Setup", "de": "Visual C++ (2005–2022) Setup"},
    "t_dx": {"tr": "DirectX, DXVK, VKD3D ve Shader Derleyicileri Kurulumu", "en": "DirectX, DXVK, VKD3D & Shader Compilers Setup", "de": "DirectX-, DXVK-, VKD3D- & Shader-Compiler-Setup"},
    "t_dotnet": {"tr": ".NET Framework 4.8 & .NET Desktop Runtime 6/8 Kurulumu", "en": ".NET Framework 4.8 & .NET Desktop Runtime 6/8 Setup", "de": ".NET Framework 4.8 & .NET Desktop Runtime 6/8 Setup"},
    "t_py": {"tr": "Windows için Python 3.12 (64-bit) Kurulumu", "en": "Python 3.12 for Windows (64-bit) Setup", "de": "Python 3.12 für Windows (64-Bit) Setup"},
    "t_java": {"tr": "Windows için Java JRE 21 LTS (64-bit) Kurulumu", "en": "Java JRE 21 LTS for Windows (64-bit) Setup", "de": "Java JRE 21 LTS für Windows (64-Bit) Setup"},
    "t_fonts": {"tr": "Yazı Tipleri (Corefonts) ve Temel DLL Kurulumu", "en": "Fonts (Corefonts) & Base DLL Setup", "de": "Schriften (Corefonts) & Basis-DLL-Setup"},
    "t_wt": {"tr": "Winetricks Kurulumu", "en": "Winetricks Setup", "de": "Winetricks-Setup"},
    "t_updates": {"tr": "Güncelleme Denetimi", "en": "Update Check", "de": "Update-Prüfung"},
    "t_rebuild": {"tr": "Yeniden Derleme", "en": "Rebuild", "de": "Neuaufbau"},
    "t_remove": {"tr": "Kaldırma", "en": "Uninstall", "de": "Deinstallation"},
}

def t(key, **kw):
    d = TRANSLATIONS.get(key)
    if not d:
        return key
    s = d.get(_LANG, d.get("en", d.get("tr", key)))
    try:
        return s.format(**kw) if kw else s
    except Exception:
        return s

# ------------------------------------------------------------------ settings
WINE_PREFIX  = os.environ.get("WINEPREFIX", os.environ.get("WINE_PREFIX", os.path.expanduser("~/.wine")))
WINE_ROOT    = "/opt/wine-patched"
WINE_BIN     = f"{WINE_ROOT}/bin/wine"
WINESERVER   = f"{WINE_ROOT}/bin/wineserver"
PKGNAME      = "wine-patched"
PKGVER       = "11.19"
WINE_SRC_URL = f"https://dl.winehq.org/wine/source/11.x/wine-{PKGVER}.tar.xz"
WORK         = os.path.expanduser("~/.cache/adobe-wine-panel")
WINE_DESKTOP = "/usr/share/applications/wine.desktop"

LOCAL_APPS_DIR = os.path.expanduser("~/.local/share/applications")
WINE_PROGS_DIR = os.path.expanduser("~/.local/share/applications/wine/Programs")
ICON_PNG_DIR   = os.path.expanduser("~/.local/share/icons/hicolor/256x256/apps")
ICON_SVG_DIR   = os.path.expanduser("~/.local/share/icons/hicolor/scalable/apps")
PIXMAPS_DIR    = os.path.expanduser("~/.local/share/pixmaps")
PANEL_DESKTOP  = os.path.join(LOCAL_APPS_DIR, "adobe-wine-panel.desktop")

MSVCP140_DLLS = (
    "msvcp140",
    "msvcp140_1",
    "msvcp140_2",
    "msvcp140_atomic_wait",
    "msvcp140_codecvt_ids",
    "vcruntime140",
)
# vcruntime140_1 and vcruntime140_threads exist only in the 64-bit package (not in x86 redist)
MSVCP140_DLLS_X64_ONLY = (
    "vcruntime140_1",
    "vcruntime140_threads",
)

# (Folder/Exe name, Display name, Subtitle, Description, Icon names, Official Adobe code[, Real Exe name])
# If no real exe name is given, the folder name is assumed (true for Substance apps).
APPS = [
    ("Adobe Substance 3D Sampler",  "Substance 3D Sampler",
     "Material authoring and capture",
     "Creates PBR materials from photos or scanned surfaces. 3D view renders via patched Wine.",
     ("substance-3d-sampler", "adobe-substance-sampler"), "Sa"),
    ("Adobe Substance 3D Designer", "Substance 3D Designer",
     "Node-based material authoring",
     "Builds and exports procedural materials with nodes. 3D view renders via patched Wine.",
     ("substance-3d-designer", "adobe-substance-designer"), "Ds"),
    ("Adobe Substance 3D Painter",  "Substance 3D Painter",
     "3D surface painting",
     "Paints directly on 3D models with brushes. NOTE: requires Adobe login on launch.",
     ("substance-3d-painter", "adobe-substance-painter"), "Pt"),
    ("Adobe Audition 2026",  "Adobe Audition",
     "Audio editing and mixing",
     "Multitrack editing, mixing and mastering. Audio via winepulse (PipeWire/PulseAudio).",
     ("adobe-audition", "substance-adobe-audition"), "Au", "Adobe Audition"),
]

def app_exe_name(t):
    """Return the real exe name of an APPS entry (folder name if 7th field is missing)."""
    return t[6] if len(t) > 6 else t[0]

PATCH_OLD = """            HANDLE shared = import_win32->handle;
            if (import_win32->name && !(shared = open_shared_resource_from_name( import_win32->name ))) break;
            memory->local = d3dkmt_open_resource( 0, shared, &memory->mutex, &memory->sync );"""

PATCH_NEW = """            HANDLE shared = import_win32->handle;
            if (import_win32->name && !(shared = open_shared_resource_from_name( import_win32->name )))
                shared = import_win32->handle;
            if (!shared) break;
            memory->local = d3dkmt_open_resource( 0, shared, &memory->mutex, &memory->sync );"""

# ------------------------------------------------------------------ helpers
def have(cmd):
    return shutil.which(cmd) is not None

def sh(cmd, **kw):
    """Run a single command, return its output."""
    try:
        return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                              text=True, **kw)
    except Exception as e:
        return e

def root_cmd(argv):
    """Run with admin rights: try sudo -n first, else pkexec."""
    if subprocess.run(["sudo", "-n", "true"], capture_output=True).returncode == 0:
        return ["sudo"] + argv
    if have("pkexec"):
        return ["pkexec"] + argv
    return ["sudo"] + argv

def cleanup_leftover_shm():
    for p in glob.glob("/dev/shm/adobe-wine-build-*"):
        try:
            shutil.rmtree(p, ignore_errors=True)
        except Exception:
            pass

GUARD_PKGS = ["wine-patched", "mingw-w64-headers", "mingw-w64-crt", "mingw-w64-winpthreads"]

def guard_ok():
    """Verify that pacman will not touch these packages."""
    try:
        with open("/etc/pacman.conf", encoding="utf-8", errors="replace") as f:
            for ln in f:
                s = ln.strip()
                if s.startswith("IgnorePkg") and all(g in s for g in GUARD_PKGS):
                    return True
    except Exception:
        pass
    return False

def apply_guard():
    """Apply the IgnorePkg guard. Success -> True."""
    if guard_ok():
        return True
    cmd = ["bash", "-c",
           "grep -q '^IgnorePkg.*wine-patched' /etc/pacman.conf || "
           "sed -i '/^\\[options\\]/a\\IgnorePkg = " + " ".join(GUARD_PKGS) + "' /etc/pacman.conf"]
    sh(root_cmd(cmd))
    return guard_ok()

# ------------------------------------------------------------------ lossless PNG and SVG icon generator
def _write_svg_icon(out_svg, badge_text, bg_hex="#133820", fg_hex="#2ee66b"):
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <rect width="228" height="228" x="14" y="14" rx="44" fill="{bg_hex}" stroke="{fg_hex}" stroke-width="8"/>
  <text x="128" y="166" text-anchor="middle" fill="{fg_hex}"
        font-family="sans-serif" font-weight="900" font-size="112">{badge_text}</text>
</svg>
"""
    os.makedirs(os.path.dirname(out_svg), exist_ok=True)
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write(svg)

def render_substance_icon_png(out_png, badge_text, bg_hex="#133820", fg_hex="#2ee66b"):
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    img = QImage(256, 256, QImage.Format.Format_ARGB32)
    img.fill(QColor(0, 0, 0, 0))

    p = QPainter()
    if not p.begin(img):
        return False
    try:
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        pen = QPen(QColor(fg_hex))
        pen.setWidth(8)
        p.setPen(pen)
        p.setBrush(QColor(bg_hex))
        p.drawRoundedRect(14, 14, 228, 228, 44.0, 44.0)

        font = QFont("Sans Serif")
        font.setPixelSize(112)
        font.setBold(True)
        p.setFont(font)
        p.setPen(QColor(fg_hex))

        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(badge_text)
        th = fm.ascent() - fm.descent()
        x = int((256 - tw) / 2)
        y = int((256 + th) / 2) - 4
        p.drawText(x, y, badge_text)
    finally:
        p.end()

    ok = img.save(out_png, "PNG")
    return bool(ok and os.path.isfile(out_png) and os.path.getsize(out_png) > 200)

def resolve_app_icon(icon_names):
    if isinstance(icon_names, str):
        icon_names = (icon_names,)
    for name in icon_names:
        for d in (ICON_PNG_DIR, PIXMAPS_DIR):
            p = os.path.join(d, f"{name}.png")
            if os.path.isfile(p) and os.path.getsize(p) > 200:
                return p
        s = os.path.join(ICON_SVG_DIR, f"{name}.svg")
        if os.path.isfile(s) and os.path.getsize(s) > 100:
            return s
    return "wine"

def shortcuts_and_icons_ok():
    if not os.path.isfile(PANEL_DESKTOP):
        return False
    for app in APPS:
        folder, _, _, _, icon_names, _ = app[:6]
        dfile = os.path.join(WINE_PROGS_DIR, f"{folder}.desktop")
        if not os.path.isfile(dfile):
            return False
        for name in icon_names:
            p = os.path.join(ICON_PNG_DIR, f"{name}.png")
            if not (os.path.isfile(p) and os.path.getsize(p) > 200):
                return False
        try:
            content = open(dfile, encoding="utf-8", errors="replace").read()
            if WINE_BIN not in content:
                return False
            m = re.search(r"^Icon=(.+)$", content, re.MULTILINE)
            if not m:
                return False
            ic_val = m.group(1).strip()
            if not (os.path.isfile(ic_val) and os.path.getsize(ic_val) > 200):
                return False
        except Exception:
            return False
    return True

def fix_shortcuts_and_icons():
    logs = []
    for d in (WINE_PROGS_DIR, LOCAL_APPS_DIR, ICON_PNG_DIR, ICON_SVG_DIR, PIXMAPS_DIR, WORK):
        os.makedirs(d, exist_ok=True)

    for pat in ("adobe-substance-*-[0-9]*.png", "adobe-wine-panel-[0-9]*.png"):
        for old_f in glob.glob(os.path.join(ICON_PNG_DIR, pat)):
            try:
                os.remove(old_f)
            except Exception:
                pass

    panel_png = os.path.join(ICON_PNG_DIR, "adobe-wine-panel.png")
    panel_svg = os.path.join(ICON_SVG_DIR, "adobe-wine-panel.svg")
    render_substance_icon_png(panel_png, "3D", bg_hex="#172554", fg_hex="#60a5fa")
    _write_svg_icon(panel_svg, "3D", bg_hex="#172554", fg_hex="#60a5fa")
    shutil.copyfile(panel_png, os.path.join(PIXMAPS_DIR, "adobe-wine-panel.png"))

    script_path = os.path.abspath(__file__)
    try:
        os.chmod(script_path, 0o755)
    except Exception:
        pass

    _pan_tr = "Adobe Substance 3D Wine Yöneticisi"
    _pan_en = "Adobe Substance 3D Wine Manager"
    _pan_de = "Adobe Substance 3D Wine-Verwaltung"
    _pan_c_tr = "Adobe Substance 3D ve Audition uygulamalarını ve yamalı Wine kurulumunu yönetir"
    _pan_c_en = "Manages Adobe Substance 3D and Audition apps and patched Wine setup"
    _pan_c_de = "Verwaltet Adobe Substance 3D- und Audition-Apps sowie gepatchtes Wine-Setup"
    panel_desk_content = f"""[Desktop Entry]
Type=Application
Name={t("window_title")}
GenericName={_pan_tr}
GenericName[tr]={_pan_tr}
GenericName[en]={_pan_en}
GenericName[de]={_pan_de}
Comment={_pan_c_tr}
Comment[tr]={_pan_c_tr}
Comment[en]={_pan_c_en}
Comment[de]={_pan_c_de}
Exec=/usr/bin/env python3 "{script_path}"
Icon={panel_png}
Terminal=false
StartupNotify=true
Categories=Graphics;3DGraphics;Settings;Utility;Audio;
Keywords=Adobe;Substance;Wine;Painter;Designer;Sampler;Audition;3D;
"""
    with open(PANEL_DESKTOP, "w", encoding="utf-8") as f:
        f.write(panel_desk_content)
    os.chmod(PANEL_DESKTOP, 0o755)
    logs.append(f"✔ Panel icon created: {panel_png}")

    app_desktop_contents = {}
    for app in APPS:
        folder, nm, sub, _, icon_names, badge_txt = app[:6]
        exe_name = app_exe_name(app)
        app_dir = f"{WINE_PREFIX}/drive_c/Program Files/Adobe/{folder}"
        if badge_txt == "Au":
            bg_hex, fg_hex = "#1e1b4b", "#22d3ee"
            cats, kw = "Audio;AudioVideo;", f"Adobe;Audition;{nm};Ses;Audio;"
        else:
            bg_hex, fg_hex = "#133820", "#2ee66b"
            cats, kw = "Graphics;3DGraphics;", f"Adobe;Substance;{nm};3D;PBR;"
        primary_png = os.path.join(ICON_PNG_DIR, f"{icon_names[0]}.png")
        ok = render_substance_icon_png(primary_png, badge_txt, bg_hex=bg_hex, fg_hex=fg_hex)
        if not ok:
            raise RuntimeError(f"{primary_png} could not be created!")

        for name in icon_names:
            dst_png = os.path.join(ICON_PNG_DIR, f"{name}.png")
            if os.path.abspath(dst_png) != os.path.abspath(primary_png):
                shutil.copyfile(primary_png, dst_png)
            shutil.copyfile(primary_png, os.path.join(PIXMAPS_DIR, f"{name}.png"))
            _write_svg_icon(os.path.join(ICON_SVG_DIR, f"{name}.svg"), badge_txt, bg_hex=bg_hex, fg_hex=fg_hex)

        wm_class = f"{exe_name.lower()}.exe"
        desk_txt = f"""[Desktop Entry]
Type=Application
Name={nm}
GenericName={sub}
Comment={sub}
Exec=env "WINEPREFIX={WINE_PREFIX}" {WINE_BIN} "C:\\\\Program Files\\\\Adobe\\\\{folder}\\\\{exe_name}.exe"
Path={app_dir}
Icon={primary_png}
Terminal=false
StartupNotify=true
StartupWMClass={wm_class}
Categories={cats}
Keywords={kw}
"""
        dfile = os.path.join(WINE_PROGS_DIR, f"{folder}.desktop")
        with open(dfile, "w", encoding="utf-8") as f:
            f.write(desk_txt)
        os.chmod(dfile, 0o755)
        app_desktop_contents[(folder, nm)] = (dfile, desk_txt)
        logs.append(f"✔ {nm} ({badge_txt}): {primary_png} ({os.path.getsize(primary_png)} bayt)")

    for root, _, files in os.walk(LOCAL_APPS_DIR):
        for fn in files:
            if not fn.endswith(".desktop"):
                continue
            full_p = os.path.abspath(os.path.join(root, fn))
            if full_p == os.path.abspath(PANEL_DESKTOP):
                continue
            try:
                txt = open(full_p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for (folder, nm), (canonical_path, new_desk_txt) in app_desktop_contents.items():
                if os.path.abspath(canonical_path) == full_p:
                    continue
                if folder in txt or nm in txt or fn == f"{folder}.desktop":
                    try:
                        with open(full_p, "w", encoding="utf-8") as f:
                            f.write(new_desk_txt)
                        os.chmod(full_p, 0o755)
                        logs.append(f"• Extra shortcut updated: {full_p}")
                    except Exception:
                        pass

    if have("update-desktop-database"):
        sh(["update-desktop-database", LOCAL_APPS_DIR])
    if have("gtk-update-icon-cache"):
        sh(["gtk-update-icon-cache", "-f", "-t", os.path.expanduser("~/.local/share/icons/hicolor")])
    for kcmd in ("kbuildsycoca6", "kbuildsycoca5"):
        if have(kcmd):
            sh([kcmd, "--noincremental"])
            break
    if have("dbus-send"):
        sh(["dbus-send", "--session", "--type=signal", "/KIconLoader",
            "org.kde.KIconLoader.iconChanged", "int32:0"])
        sh(["dbus-send", "--session", "--type=signal", "/KGlobalSettings",
            "org.kde.KGlobalSettings.notifyChange", "int32:4", "int32:0"])

    logs.append("✔ Start menu and KDE Plasma icon cache refreshed.")
    return logs

# ------------------------------------------------------------------ system and runtime scan
def wine_core_ok():
    return (
        sh(["pacman", "-Q", PKGNAME]).returncode == 0
        and os.access(WINE_BIN, os.X_OK)
        and os.access(f"{WINE_ROOT}/bin/wineserver", os.X_OK)
        and bool(glob_dll("x86_64-windows"))
        and bool(glob_dll("i386-windows"))
        and os.path.isfile(f"{WINE_ROOT}/lib/wine/x86_64-unix/win32u.so")
    )

def msvcp140_dlls_ok():
    sys32 = f"{WINE_PREFIX}/drive_c/windows/system32"
    syswow = f"{WINE_PREFIX}/drive_c/windows/syswow64"
    both = all(
        os.path.isfile(f"{sys32}/{n}.dll") and os.path.getsize(f"{sys32}/{n}.dll") > 1024
        and os.path.isfile(f"{syswow}/{n}.dll") and os.path.getsize(f"{syswow}/{n}.dll") > 1024
        for n in MSVCP140_DLLS
    )
    x64only = all(
        os.path.isfile(f"{sys32}/{n}.dll") and os.path.getsize(f"{sys32}/{n}.dll") > 1024
        for n in MSVCP140_DLLS_X64_ONLY
    )
    return both and x64only

def audio_backend_ok():
    """True if the Wine audio driver is winepulse (PipeWire/PulseAudio).

    If no Audio value is set, Wine uses its default (OK if built with pulse).
    alsa/oss/jack values break Audition.
    """
    try:
        r = sh([WINE_BIN, "reg", "query", "HKCU\\Software\\Wine\\Drivers", "/v", "Audio"],
               env=dict(os.environ, WINEPREFIX=WINE_PREFIX), timeout=10)
        out = (getattr(r, "stdout", "") or "").lower()
        if "alsa" in out or "oss" in out or "jack" in out:
            return "winepulse" in out
        return True
    except Exception:
        return True

def check_runtimes_status():
    """Check the runtime packages installed in the Wine prefix (WINEPREFIX)."""
    sys32 = f"{WINE_PREFIX}/drive_c/windows/system32"
    syswow = f"{WINE_PREFIX}/drive_c/windows/syswow64"
    pfiles = f"{WINE_PREFIX}/drive_c/Program Files"
    fonts  = f"{WINE_PREFIX}/drive_c/windows/Fonts"

    vc_ok  = msvcp140_dlls_ok()
    dx_ok  = os.path.isfile(f"{sys32}/d3dcompiler_47.dll") and os.path.isfile(f"{sys32}/d3dx9_43.dll")
    net_ok = (os.path.isdir(f"{WINE_PREFIX}/drive_c/windows/Microsoft.NET/Framework64/v4.0.30319")
              or os.path.isdir(f"{pfiles}/dotnet/shared/Microsoft.WindowsDesktop.App"))
    py_ok  = bool(glob.glob(f"{pfiles}/Python3*/python.exe")
                  or glob.glob(f"{WINE_PREFIX}/drive_c/users/*/AppData/Local/Programs/Python/Python3*/python.exe"))
    java_ok = bool(glob.glob(f"{pfiles}/Eclipse Adoptium/*/bin/java.exe")
                   or glob.glob(f"{pfiles}/Java/*/bin/java.exe"))
    fnt_ok = os.path.isfile(f"{fonts}/arial.ttf") or os.path.isfile(f"{fonts}/Arial.TTF")

    items = [
        ("Visual C++ (2005-2022) & msvcp140 DLL'leri", vc_ok),
        ("DirectX / DXVK / d3dcompiler", dx_ok),
        (".NET Framework / .NET Desktop", net_ok),
        ("Python 3 (Windows 64-bit)", py_ok),
        ("Java JRE 21 LTS (Windows 64-bit)", java_ok),
        ("Core Fonts (Corefonts)", fnt_ok),
    ]
    done_cnt = sum(1 for _, v in items if v)
    return done_cnt, len(items), items

def check_system(include_environment=False):
    ok, bad, rows = 0, 0, []
    def line(txt, cond, critical=True):
        nonlocal ok, bad
        if cond:
            ok += 1
            rows.append(("ok", txt))
        else:
            if critical:
                bad += 1
                rows.append(("bad", txt))
            else:
                rows.append(("warn", f"{txt} (optional / not installed)"))

    res = sh(["pacman", "-Q", PKGNAME])
    line("Patched Wine package (pacman)", getattr(res, "returncode", 1) == 0)
    line(f"wine executable ({WINE_BIN})", os.access(WINE_BIN, os.X_OK))
    line("wineserver present", os.access(f"{WINE_ROOT}/bin/wineserver", os.X_OK))
    line("64-bit modules (x86_64-windows)", bool(glob_dll("x86_64-windows")))
    line("32-bit modules (i386-windows)", bool(glob_dll("i386-windows")))
    line("win32u.so compiled", os.path.isfile(f"{WINE_ROOT}/lib/wine/x86_64-unix/win32u.so"))
    line("single wineserver running", count_wineserver() <= 1)
    line("wine.desktop desktop entry", os.path.isfile(WINE_DESKTOP))
    line("default .exe handler is Wine", default_exe_handler() == "wine.desktop")
    line("wine command in /usr/bin", os.access("/usr/bin/wine", os.X_OK))
    line("pacman IgnorePkg guard", guard_ok())
    line("Panel start-menu shortcut", os.path.isfile(PANEL_DESKTOP))
    line("Adobe shortcuts and icon files", shortcuts_and_icons_ok())
    line("system32+syswow64 msvcp140/vcruntime DLL'leri (7 adet x2)", msvcp140_dlls_ok(), critical=False)

    for app in APPS:
        d, nm, _, _, icon_names, _ = app[:6]
        ex = app_exe_name(app)
        dfile = os.path.join(WINE_PROGS_DIR, f"{d}.desktop")
        ic = resolve_app_icon(icon_names)
        line(f"{nm} menu shortcut and icon", os.path.isfile(dfile) and ic != "wine", critical=True)
        line(f"{nm} (.exe)", os.path.isfile(f"{WINE_PREFIX}/drive_c/Program Files/Adobe/{d}/{ex}.exe"), critical=False)
    line("Audio backend (winepulse/PipeWire)", audio_backend_ok(), critical=False)

    if include_environment:
        # Extra environment checks run only when the user requests diagnostics.
        prefix_ok = os.path.isdir(f"{WINE_PREFIX}/drive_c")
        line("Wine prefix initialized (drive_c)", prefix_ok, critical=False)
        line("Wine prefix registry files", all(
            os.path.isfile(os.path.join(WINE_PREFIX, name)) for name in ("system.reg", "user.reg")
        ), critical=False)
        try:
            disk_free_gb = shutil.disk_usage(WINE_PREFIX if os.path.isdir(WINE_PREFIX) else os.path.expanduser("~")).free / (1024 ** 3)
            line(f"Free disk space (5 GB recommended; {disk_free_gb:.1f} GB free)", disk_free_gb >= 5, critical=False)
        except OSError:
            line("Free disk space readable", False, critical=False)
        if have("vulkaninfo"):
            vk = sh(["vulkaninfo", "--summary"], timeout=4)
            line("Vulkan device accessible", getattr(vk, "returncode", 1) == 0, critical=False)
        else:
            line("Vulkan diagnostic tool (vulkaninfo)", False, critical=False)

    for r_name, r_ok in check_runtimes_status()[2]:
        line(f"Wine runtime: {r_name}", r_ok, critical=False)

    return ok, bad, rows

def glob_dll(arch):
    p = f"{WINE_ROOT}/lib/wine/{arch}"
    try:
        return [f for f in os.listdir(p) if f.endswith(".dll")][:1]
    except Exception:
        return []

def count_wineserver():
    try:
        out = subprocess.run(["pgrep", "-c", "wineserver"], capture_output=True, text=True).stdout.strip()
        return int(out) if out.isdigit() else 0
    except Exception:
        return 0

def default_exe_handler():
    try:
        return subprocess.run(["xdg-mime", "query", "default", "application/x-ms-dos-executable"],
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""

# ------------------------------------------------------------------ worker thread
class Worker(QThread):
    line = pyqtSignal(str)
    done = pyqtSignal(int)

    def __init__(self, argv, env=None):
        super().__init__()
        self.argv = argv
        self.env  = env

    def run(self):
        try:
            e = dict(os.environ)
            if self.env:
                e.update(self.env)
            p = subprocess.Popen(self.argv, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True,
                                 bufsize=1, env=e)
            for ln in p.stdout:
                self.line.emit(ln.rstrip("\n"))
            p.wait()
            self.done.emit(p.returncode)
        except Exception as ex:
            self.line.emit(f"!! {ex}")
            self.done.emit(1)

# ------------------------------------------------------------------ log window
class LogDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(880, 560)
        self.setStyleSheet("""
            QDialog { background: #1e1f22; }
            QPlainTextEdit {
                background: #17181b; color: #d7dae0; border: 1px solid #2c2e33;
                border-radius: 10px; padding: 12px;
                font-family: 'JetBrains Mono','Fira Code','DejaVu Sans Mono',monospace;
                font-size: 12px; selection-background-color: #3d5afe;
            }
            QPushButton {
                background: #2c2e33; color: #e6e8ec; border: 1px solid #3a3d43;
                border-radius: 8px; padding: 9px 22px; font-weight: 600;
            }
            QPushButton:hover { background: #3a3d43; }
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        self.view = QPlainTextEdit()
        self.view.setReadOnly(True)
        lay.addWidget(self.view, 1)

        row = QHBoxLayout()
        row.addStretch(1)
        self.ok_btn = QPushButton(t("btn_close"))
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)
        row.addWidget(self.ok_btn)
        lay.addLayout(row)

    def append(self, text):
        self.view.appendPlainText(text)
        self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().maximum())

    def finish(self, code):
        self.ok_btn.setEnabled(True)
        self.append("")
        res = t("log_result_ok") if code == 0 else t("log_result_fail", code=code)
        self.append(t("log_prefix", res=res))

    def run_async(self, argv, env=None, on_done=None):
        self.w = Worker(argv, env)
        self.w.line.connect(self.append)
        def _done(code):
            self.finish(code)
            if on_done:
                on_done(code)
        self.w.done.connect(_done)
        self.show()
        self.w.start()

# ------------------------------------------------------------------ card
class Card(QFrame):
    clicked = pyqtSignal()

    def __init__(self, icon, title, subtitle, desc, accent, theme, icon_path=None, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.accent = accent
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("card")
        self.setMinimumHeight(92)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(16)

        self.badge = QLabel()
        self.badge.setFixedSize(52, 52)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_badge(icon, icon_path)
        lay.addWidget(self.badge)

        txt = QVBoxLayout()
        txt.setSpacing(3)
        t = QLabel(title)
        t.setObjectName("cardTitle")
        s = QLabel(subtitle)
        s.setObjectName("cardSub")
        d = QLabel(desc)
        d.setObjectName("cardDesc")
        d.setWordWrap(True)
        txt.addWidget(t)
        txt.addWidget(s)
        txt.addWidget(d)
        lay.addLayout(txt, 1)

        self.arrow = QLabel("›")
        self.arrow.setObjectName("cardArrow")
        self.arrow.setFixedWidth(22)
        self.arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.arrow)

        self._apply(False)

    def _set_badge(self, fallback_text, icon_path):
        self.badge.clear()
        if icon_path and os.path.isfile(icon_path):
            pix = QPixmap(icon_path)
            if not pix.isNull():
                self.badge.setPixmap(pix.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation))
                self.badge.setStyleSheet("background: transparent; border-radius: 14px;")
                return
        self.badge.setText(fallback_text)
        self.badge.setStyleSheet(f"""
            background: {self.accent};
            border-radius: 14px;
            font-size: 20px;
            font-weight: 800;
            color: #ffffff;
        """)

    def _apply(self, hover):
        bg = self.theme["cardHover"] if hover else self.theme["card"]
        brd = self.accent if hover else self.theme["cardBorder"]
        self.setStyleSheet(f"""
            #card {{
                background: {bg};
                border: 1px solid {brd};
                border-radius: 14px;
            }}
            #cardTitle {{ color: {self.theme["fg"]}; font-size: 15px; font-weight: 700; }}
            #cardSub   {{ color: {self.accent}; font-size: 11.5px; font-weight: 600; }}
            #cardDesc  {{ color: {self.theme["muted"]}; font-size: 12px; }}
            #cardArrow {{ color: {self.theme["muted"]}; font-size: 26px; font-weight: 300; }}
        """)

    def enterEvent(self, e):
        self._apply(True)

    def leaveEvent(self, e):
        self._apply(False)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(e)

# ------------------------------------------------------------------ theme
def build_theme(app):
    win = app.palette().color(app.palette().ColorRole.Window)
    dark = win.lightness() < 128
    if dark:
        return dict(
            dark=True, bg="#15161a", panel="#1c1e23", card="#212429", cardHover="#282c33",
            cardBorder="#2e323a", fg="#f2f4f8", muted="#9aa2b1", accent="#5b8cff",
            accent2="#7c5bff", head1="#20242c", head2="#171a20", ok="#2fbf71",
            warn="#e0a33a", bad="#e05c5c", scroll="#2a2e35",
        )
    return dict(
        dark=False, bg="#f4f6fa", panel="#ffffff", card="#ffffff", cardHover="#f2f6ff",
        cardBorder="#e3e8f0", fg="#1b2130", muted="#667085", accent="#2f6bff",
        accent2="#7c3aed", head1="#2f6bff", head2="#22307a", ok="#18a558",
        warn="#c9821a", bad="#d0402f", scroll="#e6eaf2",
    )

# ------------------------------------------------------------------ main window
class Panel(QWidget):
    def __init__(self):
        super().__init__()
        cleanup_leftover_shm()
        try:
            fix_shortcuts_and_icons()
        except Exception as e:
            print("Icon creation warning:", e, file=sys.stderr)

        self.theme = build_theme(QApplication.instance())
        self.setWindowTitle(t("window_title"))
        panel_ic = resolve_app_icon("adobe-wine-panel")
        self.setWindowIcon(QIcon(panel_ic) if os.path.isfile(panel_ic) else QIcon.fromTheme("wine"))
        self.resize(900, 780)
        self.setMinimumSize(740, 580)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- header bar
        head = QFrame()
        head.setObjectName("head")
        head.setStyleSheet(f"""
            #head {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {self.theme["head1"]}, stop:1 {self.theme["head2"]});
            }}
        """)
        hl = QVBoxLayout(head)
        hl.setContentsMargins(28, 24, 28, 20)
        hl.setSpacing(6)

        title = QLabel(t("header_title"))
        title.setStyleSheet("color:#ffffff; font-size:25px; font-weight:800; letter-spacing:.3px;")
        sub = QLabel(t("header_sub"))
        sub.setStyleSheet("color: rgba(255,255,255,.82); font-size:12.5px;")
        hl.addWidget(title)
        hl.addWidget(sub)

        pill_row = QHBoxLayout()
        pill_row.setSpacing(10)
        self.pill = QLabel(t("pill_checking"))
        self.pill.setObjectName("pill")
        self.rt_pill = QLabel(t("rtpill_checking"))
        self.rt_pill.setObjectName("rt_pill")
        pill_row.addWidget(self.pill)
        pill_row.addWidget(self.rt_pill)
        pill_row.addStretch(1)
        self.lang_box = QComboBox()
        for code in LANGS:
            self.lang_box.addItem(LANG_NAMES[code], code)
        try:
            self.lang_box.setCurrentIndex(list(LANGS).index(get_lang()))
        except Exception:
            pass
        self.lang_box.setStyleSheet("background: rgba(255,255,255,.14); color:#ffffff; border:1px solid rgba(255,255,255,.35); border-radius:10px; padding:4px 10px; font-size:11.5px; font-weight:700;")
        self.lang_box.currentIndexChanged.connect(self._on_lang_changed)
        pill_row.addWidget(self.lang_box)
        hl.addLayout(pill_row)
        root.addWidget(head)

        # ---- tabbed body (QTabWidget)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {self.theme["bg"]};
            }}
            QTabBar {{
                background: {self.theme["panel"]};
            }}
            QTabBar::tab {{
                background: {self.theme["panel"]};
                color: {self.theme["muted"]};
                padding: 13px 26px;
                font-size: 13px;
                font-weight: 700;
                border: none;
                border-bottom: 3px solid transparent;
            }}
            QTabBar::tab:hover {{
                color: {self.theme["fg"]};
            }}
            QTabBar::tab:selected {{
                color: {self.theme["accent"]};
                border-bottom: 3px solid {self.theme["accent"]};
                background: {self.theme["bg"]};
            }}
        """)

        # Tab 1: Apps and System
        self.app_cards = []
        tab1 = self._build_scroll_tab(
            t("section_apps"),
            [
                ("Sa", "Substance 3D Sampler", t("c_sampler_s"),
                 t("c_sampler_d"),
                 "#2ee66b", resolve_app_icon(("substance-3d-sampler", "adobe-substance-sampler")), self.act_sampler),
                ("Ds", "Substance 3D Designer", t("c_designer_s"),
                 t("c_designer_d"),
                 "#2ee66b", resolve_app_icon(("substance-3d-designer", "adobe-substance-designer")), self.act_designer),
                ("Pt", "Substance 3D Painter", t("c_painter_s"),
                 t("c_painter_d"),
                 "#2ee66b", resolve_app_icon(("substance-3d-painter", "adobe-substance-painter")), self.act_painter),
                 ("Au", "Adobe Audition", t("c_audition_s"),
                  t("c_audition_d"),
                  "#22d3ee", resolve_app_icon(("adobe-audition", "substance-adobe-audition")), self.act_audition),
                 ("♪", t("c_audiofix_t"), t("c_audiofix_s"),
                  t("c_audiofix_d"),
                  "#14b8a6", None, self.act_audio_fix),
                ("🔧", t("c_dllfix_t"),
                 t("c_dllfix_s"),
                 t("c_dllfix_d"),
                 "#f59e0b", None, self.act_rt_dllfix),
                ("✨", t("c_shortcuts_t"), t("c_shortcuts_s"),
                 t("c_shortcuts_d"),
                 "#10b981", None, self.act_shortcuts),
                ("⚙", t("c_winecfg_t"), t("c_winecfg_s"),
                 t("c_winecfg_d"),
                 "#5b8cff", None, self.act_winecfg),
                ("🔎", t("c_diagnose_t"), t("c_diagnose_s"),
                 t("c_diagnose_d"),
                 "#38bdf8", None, self.act_diagnose),
                ("🛠", t("c_check_t"), t("c_check_s"),
                 t("c_check_d"),
                 "#2fbf71", None, self.act_check),
                ("🔄", t("c_updates_t"), t("c_updates_s"),
                 t("c_updates_d"),
                 "#e05c9a", None, self.act_updates),
                ("🔁", t("c_rebuild_t"), t("c_rebuild_s"),
                 t("c_rebuild_d"),
                 "#8a6d3b", None, self.act_rebuild),
                ("🛡", t("c_guard_t"), t("c_guard_s"),
                 t("c_guard_d"),
                 "#4b5bdc", None, self.act_guard),
                ("🗑", t("c_uninstall_t"), t("c_uninstall_s"),
                 t("c_uninstall_d"),
                 "#d0402f", None, self.act_uninstall),
            ],
            collect_app_cards=True
        )

        # Tab 2: Runtimes (VCRedist, DLL Fix, .NET, DirectX, Java, Python)
        tab2 = self._build_scroll_tab(
            t("section_reqs"),
            [
                ("🚀", t("r_all_t"),
                 t("r_all_s"),
                 t("r_all_d"),
                 "#10b981", None, self.act_rt_all),
                ("🔧", t("c_dllfix_t"),
                 t("r_dllfix_s"),
                 t("r_dllfix_d"),
                 "#f59e0b", None, self.act_rt_dllfix),
                ("C++", t("r_vc_t"),
                 t("r_vc_s"),
                 t("r_vc_d"),
                 "#3b82f6", None, self.act_rt_vcredist),
                ("DX", t("r_dx_t"),
                 t("r_dx_s"),
                 t("r_dx_d"),
                 "#8b5cf6", None, self.act_rt_directx),
                (".NET", t("r_dot_t"),
                 t("r_dot_s"),
                 t("r_dot_d"),
                 "#6366f1", None, self.act_rt_dotnet),
                ("Py", t("r_py_t"),
                 t("r_py_s"),
                 t("r_py_d"),
                 "#eab308", None, self.act_rt_python),
                ("Jv", t("r_java_t"),
                 t("r_java_s"),
                 t("r_java_d"),
                 "#f97316", None, self.act_rt_java),
                ("Aa", t("r_fonts_t"),
                 t("r_fonts_s"),
                 t("r_fonts_d"),
                 "#14b8a6", None, self.act_rt_fonts_dlls),
                ("🧰", t("r_wt_t"),
                 t("r_wt_s"),
                 t("r_wt_d"),
                 "#ec4899", None, self.act_rt_winetricks_gui),
            ],
            collect_app_cards=False
        )

        self.tabs.addTab(tab1, t("tab_apps"))
        self.tabs.addTab(tab2, t("tab_reqs"))
        root.addWidget(self.tabs, 1)

        # ---- footer
        foot = QFrame()
        foot.setObjectName("foot")
        foot.setStyleSheet(f"background:{self.theme['panel']}; border-top:1px solid {self.theme['cardBorder']};")
        fl = QHBoxLayout(foot)
        fl.setContentsMargins(26, 14, 26, 14)
        note = QLabel(f"{t('footer_install')} <b>{WINE_ROOT}</b>   ·   {t('footer_prefix')} <b>{WINE_PREFIX}</b>")
        note.setStyleSheet(f"color:{self.theme['muted']}; font-size:11px;")
        fl.addWidget(note)
        fl.addStretch(1)
        about = QPushButton(t("btn_about"))
        about.setObjectName("ghost")
        about.clicked.connect(self.act_about)
        close = QPushButton(t("btn_close"))
        close.setObjectName("primary")
        close.clicked.connect(self.close)
        fl.addWidget(about)
        fl.addWidget(close)
        for b, kind in ((about, "ghost"), (close, "primary")):
            b.setStyleSheet(self._btn_css(kind))
            b.setFixedHeight(38)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        root.addWidget(foot)

        self.refresh_status()
        QTimer.singleShot(400, self._startup_check)

    def _build_scroll_tab(self, section_title, items, collect_app_cards=False):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: {self.theme["bg"]}; border:none; }}
            QScrollBar:vertical {{
                background: transparent; width: 11px; margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.theme["scroll"]}; border-radius: 5px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        body = QWidget()
        body.setStyleSheet(f"background: {self.theme['bg']};")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(26, 20, 26, 22)
        bl.setSpacing(12)

        lbl = QLabel(section_title)
        lbl.setStyleSheet(f"color:{self.theme['muted']}; font-size:11px; font-weight:800; letter-spacing:1.3px;")
        bl.addWidget(lbl)

        for ic, t, s, d, acc, ic_path, fn in items:
            c = Card(ic, t, s, d, acc, self.theme, icon_path=ic_path)
            c.clicked.connect(fn)
            bl.addWidget(c)
            if collect_app_cards and ic in ("Sa", "Ds", "Pt"):
                self.app_cards.append((ic, c))

        bl.addStretch(1)
        scroll.setWidget(body)
        return scroll

    def _refresh_card_icons(self):
        mapping = {
            "Sa": resolve_app_icon(("substance-3d-sampler", "adobe-substance-sampler")),
            "Ds": resolve_app_icon(("substance-3d-designer", "adobe-substance-designer")),
            "Pt": resolve_app_icon(("substance-3d-painter", "adobe-substance-painter")),
        }
        for code, card in self.app_cards:
            card._set_badge(code, mapping.get(code))

    def _startup_check(self):
        try:
            ok, bad, _ = check_system()
        except Exception:
            return
        if bad == 0:
            return
        if self._ask(t("d_startup_t"),
                     t("d_startup_n", bad=bad) + " " + t("d_startup_b")):
            self.act_check()

    def _btn_css(self, kind):
        t = self.theme
        if kind == "primary":
            return f"""
                QPushButton {{ background: {t["accent"]}; color:#fff; border:none;
                               border-radius:9px; padding:0 22px; font-weight:700; font-size:13px; }}
                QPushButton:hover {{ background: {t["accent2"]}; }}
                QPushButton:pressed {{ background: {t["head2"]}; }}"""
        return f"""
            QPushButton {{ background: transparent; color:{t["muted"]};
                           border:1px solid {t["cardBorder"]}; border-radius:9px;
                           padding:0 18px; font-size:13px; }}
            QPushButton:hover {{ color:{t["fg"]}; border-color:{t["accent"]}; }}"""

    def refresh_status(self):
        ok, bad, _ = check_system()
        rt_done, rt_total, _ = check_runtimes_status()
        self._refresh_card_icons()
        if bad == 0:
            self.pill.setText(t("pill_ready", ok=ok))
            self.pill.setStyleSheet(self._pill_css(self.theme["ok"]))
        else:
            self.pill.setText(t("pill_missing", bad=bad))
            self.pill.setStyleSheet(self._pill_css(self.theme["warn"]))

        if rt_done == rt_total:
            self.rt_pill.setText(t("rtpill_done", d=rt_done, t=rt_total))
            self.rt_pill.setStyleSheet(self._pill_css(self.theme["ok"]))
        else:
            self.rt_pill.setText(t("rtpill_partial", d=rt_done, t=rt_total))
            self.rt_pill.setStyleSheet(self._pill_css(self.theme["accent"]))

    def _on_lang_changed(self, idx):
        try:
            code = self.lang_box.itemData(idx)
            if not code or code == get_lang():
                return
            set_lang(code)
            self._msg(t("d_lang_restart_t"), t("d_lang_restart_b"))
            try:
                os.execv(sys.executable, [sys.executable, os.path.abspath(__file__)] + sys.argv[1:])
            except Exception:
                pass
            self.refresh_status()
            try:
                self.setWindowTitle(t("window_title"))
                self.tabs.setTabText(0, t("tab_apps"))
                self.tabs.setTabText(1, t("tab_reqs"))
            except Exception:
                pass
        except Exception:
            pass

    def _pill_css(self, color):
        return (f"background: rgba(255,255,255,.14); color:#ffffff;"
                f" border:1px solid {color}; border-radius:15px;"
                f" padding:6px 14px; font-size:11.5px; font-weight:700;")

    def _run_script(self, title, script, after=None):
        dlg = LogDialog(title, self)
        dlg.run_async(["bash", "-c", script], on_done=after)
        dlg.exec()
        try:
            fix_shortcuts_and_icons()
        except Exception:
            pass
        self.refresh_status()

    def _require_wine(self):
        if not os.access(WINE_BIN, os.X_OK):
            self._msg(t("d_wine_missing_t"),
                      f"<b>{WINE_BIN}</b> yok.<br><br>" + t("d_wine_missing_b"), True)
            return False
        return True

    def _launch(self, folder, name, exe_name=None):
        if not self._require_wine():
            return
        ex = exe_name or folder
        exe = f"{WINE_PREFIX}/drive_c/Program Files/Adobe/{folder}/{ex}.exe"
        if not os.path.isfile(exe):
            self._msg(f"{name} " + t("d_notfound_suf"),
                      f"<b>{exe}</b> not found.<br><br>" + t("d_notfound_b"), True)
            return
        env = dict(os.environ, WINEPREFIX=WINE_PREFIX)
        subprocess.Popen([WINE_BIN, f"C:\\Program Files\\Adobe\\{folder}\\{ex}.exe"],
                         cwd=f"{WINE_PREFIX}/drive_c/Program Files/Adobe/{folder}",
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        self._msg(f"{name} " + t("d_started_suf"),
                  t("d_started_b"))

    def act_sampler(self):  self._launch("Adobe Substance 3D Sampler",  "Substance 3D Sampler")
    def act_designer(self): self._launch("Adobe Substance 3D Designer", "Substance 3D Designer")
    def act_painter(self):  self._launch("Adobe Substance 3D Painter",  "Substance 3D Painter")
    def act_audition(self): self._launch("Adobe Audition 2026", "Adobe Audition", "Adobe Audition")

    def act_audio_fix(self):
        """Audition-specific repair: pin audio backend to winepulse + rebuild shortcuts."""
        if not self._require_wine():
            return
        env = dict(os.environ, WINEPREFIX=WINE_PREFIX)
        sh([WINE_BIN, "reg", "add", "HKCU\\Software\\Wine\\Drivers",
            "/v", "Audio", "/d", "winepulse.drv", "/f"], env=env)
        try:
            logs = fix_shortcuts_and_icons()
            details = "<br>".join(logs)
        except Exception as ex:
            self._msg(t("d_error_t"), t("d_audio_err") + f"<br><br><tt>{ex}</tt>", True)
            return
        self.refresh_status()
        ok = audio_backend_ok()
        self._msg(t("d_audio_done") if ok else t("d_audio_check"),
                  t("d_audio_b") + f"<br><br>{details}<br><br>"
                  + t("d_audio_reopen"), not ok)

    # ---------------------------------------------------------- 2. sekme eylemleri (Gereksinimler & DLL Fix)
    def act_rt_all(self):
        if not self._require_wine():
            return
        if not self._ask(t("d_rtall_t"),
                         t("d_rtall_q", prefix=WINE_PREFIX)):
            return
        self._run_script(t("t_all_rt"), RT_ALL_SCRIPT)

    def act_rt_dllfix(self):
        if not self._require_wine():
            return
        self._run_script(t("t_dllfix"), RT_DLLFIX_SCRIPT)

    def act_rt_vcredist(self):
        if not self._require_wine():
            return
        self._run_script(t("t_vc"), RT_VCREDIST_SCRIPT)

    def act_rt_directx(self):
        if not self._require_wine():
            return
        self._run_script(t("t_dx"), RT_DIRECTX_SCRIPT)

    def act_rt_dotnet(self):
        if not self._require_wine():
            return
        self._run_script(t("t_dotnet"), RT_DOTNET_SCRIPT)

    def act_rt_python(self):
        if not self._require_wine():
            return
        self._run_script(t("t_py"), RT_PYTHON_SCRIPT)

    def act_rt_java(self):
        if not self._require_wine():
            return
        self._run_script(t("t_java"), RT_JAVA_SCRIPT)

    def act_rt_fonts_dlls(self):
        if not self._require_wine():
            return
        self._run_script(t("t_fonts"), RT_FONTS_DLL_SCRIPT)

    def act_rt_winetricks_gui(self):
        if not self._require_wine():
            return
        if not have("winetricks"):
            self._run_script(t("t_wt"), RT_PREP_HEADER + "\necho '✔ winetricks ready.'\n")
        env = dict(os.environ, WINEPREFIX=WINE_PREFIX, WINE=WINE_BIN, WINESERVER=WINESERVER)
        subprocess.Popen(["winetricks", "--gui"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)

    # ---------------------------------------------------------- 1. sekme eylemleri
    def act_shortcuts(self):
        try:
            logs = fix_shortcuts_and_icons()
            self.refresh_status()
            details = "<br>".join(logs)
            if self._ask(t("d_shortcuts_t"),
                         t("d_shortcuts_gen") + f"<br><br>{details}<br><br>"
                         + t("d_shortcuts_q")):
                subprocess.Popen(["bash", "-c", "kbuildsycoca6 --noincremental >/dev/null 2>&1; "
                                                "systemctl --user restart plasma-plasmashell.service 2>/dev/null || "
                                                "(kquitapp6 plasmashell && kstart6 plasmashell) >/dev/null 2>&1"])
        except Exception as ex:
            self._msg(t("d_error_t"), t("d_shortcuts_err") + f"<br><br><tt>{ex}</tt>", True)

    def act_winecfg(self):
        if not self._require_wine():
            return
        env = dict(os.environ, WINEPREFIX=WINE_PREFIX)
        subprocess.Popen([f"{WINE_ROOT}/bin/winecfg"], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, env=env)

    def act_check(self):
        try:
            apply_guard()
            fix_shortcuts_and_icons()
        except Exception:
            pass
        ok, bad, rows = check_system()
        icons = {"ok": "✔", "bad": "✘", "warn": "⚠"}
        details = "<br>".join(f"{icons.get(k, '•')} {v}" for k, v in rows)
        if bad == 0:
            self._msg(t("d_check_ok_t"),
                      t("d_check_ok_b") + f"<br><br>{details}")
            self.refresh_status()
            return

        if wine_core_ok():
            if not self._ask(t("d_cfg_missing_t"),
                             t("d_cfg_build_ok", bad=bad) + f"<br><br>{details}<br><br>"
                             + t("d_cfg_missing_q")):
                return
            self._run_script(t("t_quick_repair"), QUICK_REPAIR_SCRIPT)
            return

        if not self._ask(t("d_missing_t"),
                         t("d_missing_n", bad=bad) + f"<br><br>{details}<br><br>"
                         + t("d_missing_q")):
            return
        self._run_script(t("t_sys_repair"), REPAIR_SCRIPT)

    def act_diagnose(self):
        """Read-only: scan for issues and suggest the matching panel action."""
        try:
            ok, bad, rows = check_system(include_environment=True)
            _, _, runtime_rows = check_runtimes_status()
        except Exception as exc:
            self._msg(t("d_diag_fail_t"),
                      t("d_diag_fail_b") + f"<br><br><tt>{exc}</tt>", True)
            return

        from html import escape
        icons = {"ok": "✔", "bad": "✘", "warn": "⚠"}
        safe_rows = [(status, escape(text)) for status, text in rows]
        issues = [(status, text) for status, text in safe_rows if status != "ok"]
        missing_rt = [escape(name) for name, present in runtime_rows if not present]
        guidance = []
        for status, text in issues:
            low = text.lower()
            if "vulkan" in low:
                guidance.append(t("g_vulkan"))
            elif "disk" in low or "space" in low:
                guidance.append(t("g_disk"))
            elif "prefix" in low:
                guidance.append(t("g_prefix"))
            elif "audio" in low:
                guidance.append(t("g_audio"))
            elif "runtime" in low or any(rt.lower() in low for rt in missing_rt):
                guidance.append(t("g_rt"))
            elif status == "bad":
                guidance.append(t("g_crit"))
            elif "shortcut" in low or "icon" in low:
                guidance.append(t("g_short"))
        guidance = list(dict.fromkeys(guidance))
        details = "<br>".join(f"{icons.get(status, '•')} {text}" for status, text in safe_rows)
        if not guidance:
            guidance = [t("d_diag_none")]
        self._msg(t("d_diag_t"),
                  t("d_diag_b", ok=ok, bad=bad, n=len(issues)) + f"<br><br>{details}<br><br>"
                  + t("d_diag_steps") + "<br>• " + "<br>• ".join(guidance))
        self.refresh_status()

    def act_updates(self):
        self._run_script(t("t_updates"), UPDATE_SCRIPT)

    def act_rebuild(self):
        if not self._ask(t("d_rebuild_t"),
                         t("d_rebuild_b")):
            return
        self._run_script(t("t_rebuild"), REBUILD_SCRIPT)

    def _confirm_word(self, title, word, html):
        txt, ok = QInputDialog.getText(self, title,
            html + "<br><br>" + t("d_uninstall_confirm", w=word),
            text="")
        return ok and txt.strip() == word

    def act_guard(self):
        if apply_guard():
            self._msg(t("d_guard_ok_t"),
                      t("d_guard_ok_b") + "<br><br>"
                      + "".join(f"• <tt>{g}</tt><br>" for g in GUARD_PKGS) +
                      "<br>" + t("d_guard_ok_f"))
        else:
            self._msg(t("d_guard_fail_t"),
                      t("d_guard_fail_b"), True)

    def act_uninstall(self):
        if not self._confirm_word(t("d_uninstall_t"), t("d_uninstall_word"),
                                  t("d_uninstall_b")):
            return
        self._run_script(t("t_remove"), UNINSTALL_SCRIPT)

    def act_about(self):
        self._msg(t("window_title"),
                  t("d_about_b") + f"<br><br>"
                  f"<b>{t('footer_install')}</b> <tt>{WINE_ROOT}</tt><br>"
                  f"<b>{t('footer_prefix')}</b> <tt>{WINE_PREFIX}</tt><br>"
                  f"<b>Icons:</b> <tt>{ICON_PNG_DIR}</tt><br>"
                  f"<b>Shortcuts:</b> <tt>{WINE_PROGS_DIR}</tt>")

    def _msg(self, title, html, err=False):
        b = QMessageBox(self)
        b.setWindowTitle(title)
        b.setIcon(QMessageBox.Icon.Critical if err else QMessageBox.Icon.Information)
        b.setTextFormat(Qt.TextFormat.RichText)
        b.setText(html)
        b.setStyleSheet(self._msg_css())
        b.exec()

    def _ask(self, title, html):
        b = QMessageBox(self)
        b.setWindowTitle(title)
        b.setIcon(QMessageBox.Icon.Question)
        b.setTextFormat(Qt.TextFormat.RichText)
        b.setText(html)
        b.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        b.button(QMessageBox.StandardButton.Yes).setText(t("btn_yes"))
        b.button(QMessageBox.StandardButton.No).setText(t("btn_no"))
        b.setStyleSheet(self._msg_css())
        return b.exec() == QMessageBox.StandardButton.Yes

    def _msg_css(self):
        t = self.theme
        return f"""
            QMessageBox {{ background: {t["panel"]}; }}
            QLabel {{ color: {t["fg"]}; font-size: 13px; }}
            QPushButton {{ background: {t["accent"]}; color:#fff; border:none;
                           border-radius:8px; padding:8px 20px; font-weight:600; min-width:80px; }}
            QPushButton:hover {{ background: {t["accent2"]}; }}"""

# ------------------------------------------------------------------ Wine runtime scripts
RT_PREP_HEADER = f'''
set -u
export WINEPREFIX="{WINE_PREFIX}"
export WINE="{WINE_BIN}"
export WINESERVER="{WINESERVER}"
export WINEDEBUG="-all"
RT_CACHE="{WORK}/runtimes"
mkdir -p "$RT_CACHE"

if ! command -v winetricks >/dev/null 2>&1 || ! command -v cabextract >/dev/null 2>&1; then
  echo "▸ Checking system packages (winetricks, cabextract, unzip, curl)..."
  if sudo -n true 2>/dev/null; then ROOTCMD=(sudo); elif command -v pkexec >/dev/null; then ROOTCMD=(pkexec); else ROOTCMD=(sudo); fi
  ${{ROOTCMD[@]}} pacman -S --needed --noconfirm winetricks cabextract unzip p7zip curl wget zenity
fi

echo "▸ Preparing Wine prefix ({WINE_PREFIX}) and setting Windows 11 mode..."
"{WINE_BIN}" wineboot -u 2>/dev/null || true
winetricks -q win11 2>/dev/null || true
"{WINE_BIN}" reg add 'HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion' /v CurrentBuildNumber /d 26300 /f 2>/dev/null || true
"{WINE_BIN}" reg add 'HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion' /v CurrentBuild /d 26300 /f 2>/dev/null || true
"{WINE_BIN}" reg add 'HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion' /v DisplayVersion /d 26H2 /f 2>/dev/null || true
'''

RT_DLLFIX_BODY = '''
echo "════════════════════════════════════════════════════════════"
echo "▸ msvcp140 + vcruntime140 (VC++ 2022 x64+x86) Direct DLL Repair"
echo "════════════════════════════════════════════════════════════"
SYS32="$WINEPREFIX/drive_c/windows/system32"
SYSWOW="$WINEPREFIX/drive_c/windows/syswow64"
SRC64="/tmp/vc64/out"
SRC86="/tmp/vc86/out"
WT_X64="$HOME/.cache/winetricks/vcrun2022/vc_redist.x64.exe"
WT_X86="$HOME/.cache/winetricks/vcrun2022/vc_redist.x86.exe"
VC_X64=""
VC_X86=""
DLLS_COMMON="msvcp140 msvcp140_1 msvcp140_2 msvcp140_atomic_wait msvcp140_codecvt_ids vcruntime140 vcruntime140_threads"
DLLS_X64ONLY="vcruntime140_1"
DLLS="$DLLS_COMMON $DLLS_X64ONLY"

mkdir -p "$SYS32" "$SYSWOW"

if [[ -s "$WT_X64" ]]; then
  VC_X64="$WT_X64"
  echo "  -> Found vc_redist.x64.exe in winetricks cache."
elif [[ -s "$RT_CACHE/vc_redist.x64.exe" ]]; then
  VC_X64="$RT_CACHE/vc_redist.x64.exe"
  echo "  -> Found vc_redist.x64.exe in panel cache."
else
  echo "  -> Downloading vc_redist.x64.exe..."
  mkdir -p "$HOME/.cache/winetricks/vcrun2022"
  curl -fL -o "$HOME/.cache/winetricks/vcrun2022/vc_redist.x64.exe" "https://aka.ms/vs/17/release/vc_redist.x64.exe"
  VC_X64="$HOME/.cache/winetricks/vcrun2022/vc_redist.x64.exe"
fi

if [[ -s "$WT_X86" ]]; then
  VC_X86="$WT_X86"
  echo "  -> Found vc_redist.x86.exe in winetricks cache."
elif [[ -s "$RT_CACHE/vc_redist.x86.exe" ]]; then
  VC_X86="$RT_CACHE/vc_redist.x86.exe"
  echo "  -> Found vc_redist.x86.exe in panel cache."
else
  echo "  -> Downloading vc_redist.x86.exe (needed for syswow64)..."
  mkdir -p "$HOME/.cache/winetricks/vcrun2022"
  curl -fL -o "$HOME/.cache/winetricks/vcrun2022/vc_redist.x86.exe" "https://aka.ms/vs/17/release/vc_redist.x86.exe"
  VC_X86="$HOME/.cache/winetricks/vcrun2022/vc_redist.x86.exe"
fi

echo "  -> Extracting /tmp/vc64 (x64)..."
rm -rf /tmp/vc64
mkdir -p "$SRC64"
cd /tmp/vc64
cabextract -q "$VC_X64"
for f in a*; do
  [[ -f "$f" ]] && cabextract -q -d out "$f" -F '*msvcp140*' 2>/dev/null || true
  [[ -f "$f" ]] && cabextract -q -d out "$f" -F '*vcruntime140*' 2>/dev/null || true
done

echo "  -> Extracting /tmp/vc86 (x86)..."
rm -rf /tmp/vc86
mkdir -p "$SRC86"
cd /tmp/vc86
cabextract -q "$VC_X86"
for f in a*; do
  [[ -f "$f" ]] && cabextract -q -d out "$f" -F '*msvcp140*' 2>/dev/null || true
  [[ -f "$f" ]] && cabextract -q -d out "$f" -F '*vcruntime140*' 2>/dev/null || true
done

echo "  -> Copying 64-bit DLLs to system32..."
for n in $DLLS_COMMON $DLLS_X64ONLY; do
  if [[ -f "$SRC64/${n}.dll_amd64" ]]; then
    cp -f "$SRC64/${n}.dll_amd64" "$SYS32/${n}.dll"
    echo "     ✔ ${n}.dll_amd64 -> system32/${n}.dll"
  elif [[ -f "$SRC64/${n}.dll" ]]; then
    cp -f "$SRC64/${n}.dll" "$SYS32/${n}.dll"
    echo "     ✔ ${n}.dll -> system32/${n}.dll"
  else
    echo "     ! Warning: ${n} (x64) source not found!"
  fi
done

echo "  -> Copying 32-bit DLLs to syswow64 (vcruntime140_1 has no x86, skipped)..."
for n in $DLLS_COMMON; do
  if [[ -f "$SRC86/${n}.dll_x86" ]]; then
    cp -f "$SRC86/${n}.dll_x86" "$SYSWOW/${n}.dll"
    echo "     ✔ ${n}.dll_x86 -> syswow64/${n}.dll"
  elif [[ -f "$SRC86/${n}.dll" ]]; then
    cp -f "$SRC86/${n}.dll" "$SYSWOW/${n}.dll"
    echo "     ✔ ${n}.dll -> syswow64/${n}.dll"
  else
    echo "     ! Warning: ${n} (x86) source not found!"
  fi
done

echo "  -> Setting DLL overrides to native,builtin..."
for n in $DLLS; do
  "$WINE" reg add 'HKCU\\Software\\Wine\\DllOverrides' /v "*${n}" /d 'native,builtin' /f 2>/dev/null || true
done

echo "  -> system32 status:"
ls -l "$SYS32"/msvcp140*.dll "$SYS32"/vcruntime140*.dll
echo "  -> syswow64 status:"
ls -l "$SYSWOW"/msvcp140*.dll "$SYSWOW"/vcruntime140*.dll

echo "  -> Restarting wineserver (-k)..."
"$WINESERVER" -k 2>/dev/null || true
echo "✔ msvcp140+vcruntime140 direct DLL repair done (x64+x86)."
'''

RT_VCREDIST_BODY = '''
echo "════════════════════════════════════════════════════════════"
echo "▸ Installing Visual C++ Redistributable (2005-2022) packages"
echo "════════════════════════════════════════════════════════════"
for pkg in vcrun2005 vcrun2008 vcrun2010 vcrun2012 vcrun2013 vcrun2022; do
  echo "  -> Installing $pkg..."
  winetricks -q --force "$pkg" || echo "  ! $pkg returned a winetricks warning, continuing..."
done

echo "  -> Verifying latest Microsoft VC++ 2015-2022 (x86 and x64) directly..."
curl -fL -o "$RT_CACHE/vc_redist.x64.exe" "https://aka.ms/vs/17/release/vc_redist.x64.exe" \
  && "$WINE" "$RT_CACHE/vc_redist.x64.exe" /install /quiet /norestart || true
curl -fL -o "$RT_CACHE/vc_redist.x86.exe" "https://aka.ms/vs/17/release/vc_redist.x86.exe" \
  && "$WINE" "$RT_CACHE/vc_redist.x86.exe" /install /quiet /norestart || true
"$WINESERVER" -w || true
echo "✔ Visual C++ 2005-2022 setup done."
''' + RT_DLLFIX_BODY

RT_DIRECTX_BODY = '''
echo "════════════════════════════════════════════════════════════"
echo "▸ Installing DirectX 9/10/11/12, DXVK, VKD3D and HLSL compilers"
echo "════════════════════════════════════════════════════════════"
for dxpkg in d3dx9 d3dx10 d3dx11_43 d3dcompiler_43 d3dcompiler_47 dxvk vkd3d; do
  echo "  -> Installing $dxpkg..."
  winetricks -q "$dxpkg" || echo "  ! Warning during $dxpkg install, continuing..."
done
"$WINESERVER" -w || true
echo "✔ DirectX, DXVK and VKD3D setup done."
'''

RT_DOTNET_BODY = '''
echo "════════════════════════════════════════════════════════════"
echo "▸ Installing Microsoft .NET Desktop Runtime (6.0 & 8.0) and .NET 4.8"
echo "════════════════════════════════════════════════════════════"
echo "  -> Removing wine-mono (to avoid conflict with real Microsoft .NET)..."
"$WINE" uninstaller --remove "{E45D8920-A758-4088-B6C6-31DBB276992E}" 2>/dev/null || true

echo "  -> Downloading and installing Microsoft .NET Desktop Runtime 8.0 LTS (x64)..."
DOTNET8_URL="https://builds.dotnet.microsoft.com/dotnet/WindowsDesktop/8.0.15/windowsdesktop-runtime-8.0.15-win-x64.exe"
curl -fL -o "$RT_CACHE/windowsdesktop-runtime-8-x64.exe" "$DOTNET8_URL" \
  && "$WINE" "$RT_CACHE/windowsdesktop-runtime-8-x64.exe" /install /quiet /norestart || true

echo "  -> Downloading and installing Microsoft .NET Desktop Runtime 6.0 LTS (x64)..."
DOTNET6_URL="https://builds.dotnet.microsoft.com/dotnet/WindowsDesktop/6.0.36/windowsdesktop-runtime-6.0.36-win-x64.exe"
curl -fL -o "$RT_CACHE/windowsdesktop-runtime-6-x64.exe" "$DOTNET6_URL" \
  && "$WINE" "$RT_CACHE/windowsdesktop-runtime-6-x64.exe" /install /quiet /norestart || true

echo "  -> Installing classic .NET Framework 4.8 (dotnet48) (may take a few minutes)..."
winetricks -q dotnet48 || true
"$WINE" winecfg -v win10 2>/dev/null || true
"$WINESERVER" -w || true
echo "✔ .NET Framework and .NET Desktop Runtime setups done."
'''

RT_PYTHON_BODY = '''
echo "════════════════════════════════════════════════════════════"
echo "▸ Installing Python 3.12 for Windows (64-bit) and PIP"
echo "════════════════════════════════════════════════════════════"
PY_URL="https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
echo "  -> Downloading Python 3.12.8 (64-bit)..."
curl -fL -o "$RT_CACHE/python-3.12.8-amd64.exe" "$PY_URL"
echo "  -> Silent install into Wine prefix (PrependPath=1, Include_pip=1)..."
"$WINE" "$RT_CACHE/python-3.12.8-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 || true
"$WINESERVER" -w || true
echo "✔ Windows Python 3.12 setup done."
'''

RT_JAVA_BODY = '''
echo "════════════════════════════════════════════════════════════"
echo "▸ Installing Eclipse Temurin Java JRE 21 LTS (Windows 64-bit)"
echo "════════════════════════════════════════════════════════════"
JAVA_API="https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jre/hotspot/normal/eclipse?project=jdk"
echo "  -> Downloading Temurin JRE 21 LTS (x64)..."
curl -fL -o "$RT_CACHE/temurin-jre21-win64.msi" "https://api.adoptium.net/v3/installer/latest/21/ga/windows/x64/jre/hotspot/normal/eclipse" \
  && "$WINE" msiexec /i "$RT_CACHE/temurin-jre21-win64.msi" INSTALLLEVEL=1 /quiet /norestart || true
"$WINESERVER" -w || true
echo "✔ Windows Java JRE 21 LTS setup done."
'''

RT_FONTS_DLL_BODY = '''
echo "════════════════════════════════════════════════════════════"
echo "▸ Installing core Windows fonts (Corefonts) and system DLL packages"
echo "════════════════════════════════════════════════════════════"
for fpkg in corefonts tahoma gdiplus msxml3 msxml6 winhttp ucrtbase; do
  echo "  -> Installing $fpkg..."
  winetricks -q "$fpkg" || true
done
echo "  -> Setting msxml3 override to builtin (native msxml3 cannot load as COM without msxml3r in system32)..."
"$WINE" reg add 'HKCU\\Software\\Wine\\DllOverrides' /v '*msxml3' /d 'builtin' /f 2>/dev/null || true
"$WINE" winecfg -v win11 2>/dev/null || true
"$WINE" reg add 'HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion' /v CurrentBuildNumber /d 26300 /f 2>/dev/null || true
"$WINE" reg add 'HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion' /v DisplayVersion /d 26H2 /f 2>/dev/null || true
"$WINESERVER" -w || true
echo "✔ Fonts and system DLL components done."
'''

RT_DLLFIX_SCRIPT    = RT_PREP_HEADER + RT_DLLFIX_BODY
RT_VCREDIST_SCRIPT  = RT_PREP_HEADER + RT_VCREDIST_BODY
RT_DIRECTX_SCRIPT   = RT_PREP_HEADER + RT_DIRECTX_BODY
RT_DOTNET_SCRIPT    = RT_PREP_HEADER + RT_DOTNET_BODY
RT_PYTHON_SCRIPT    = RT_PREP_HEADER + RT_PYTHON_BODY
RT_JAVA_SCRIPT      = RT_PREP_HEADER + RT_JAVA_BODY
RT_FONTS_DLL_SCRIPT = RT_PREP_HEADER + RT_FONTS_DLL_BODY

RT_ALL_SCRIPT = (
    RT_PREP_HEADER
    + RT_FONTS_DLL_BODY
    + RT_VCREDIST_BODY
    + RT_DIRECTX_BODY
    + RT_PYTHON_BODY
    + RT_JAVA_BODY
    + RT_DOTNET_BODY
    + '\necho ""\necho "🎉 ALL WINE RUNTIMES AND DLL REPAIRS INSTALLED SUCCESSFULLY!"\n'
)

# ------------------------------------------------------------------ Wine build scripts
PATCH_PY = r'''
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8", errors="replace").read()
OLD = %r
NEW = %r
if NEW in s:
    print("   patch already applied."); sys.exit(0)
n = s.count(OLD)
if n != 1:
    print("   !! patch pattern not found (matches=%%d). Wine version may have changed." %% n)
    sys.exit(2)
open(p, "w", encoding="utf-8").write(s.replace(OLD, NEW))
print("   patch applied -> dlls/win32u/vulkan.c")
''' % (PATCH_OLD, PATCH_NEW)

PKG_MAKE = f'''
mkdir -p "$WORK/pkg"
cat > "$WORK/pkg/PKGBUILD" <<PKGE
pkgname={PKGNAME}
pkgver={PKGVER}
pkgrel=1
pkgdesc="Wine {PKGVER} with win32u shared-resource fix for VK_KHR_external_memory_win32"
arch=('x86_64')
url="https://www.winehq.org/"
license=('LGPL-2.1-or-later')
provides=('wine')
options=('!strip' 'emptydirs')
source=()
md5sums=()
package() {{
  cp -a "$WORK/dest/." "\\$pkgdir/"
  find "\\$pkgdir{WINE_ROOT}" -type f \\( -name '*.so' -o -name '*.dll' -o -name '*.exe' \\) \\
    -exec strip --strip-unneeded {{}} + 2>/dev/null || true
  install -d "\\$pkgdir/usr/bin"
  local _t
  for _t in wine wineserver winecfg wineboot wineconsole winedbg winefile \\
           winepath winemine regedit regsvr32 msiexec msidb notepad \\
           winebuild winegcc wineg++ winecpp winemaker winedump widl wmc wrc; do
    ln -s {WINE_ROOT}/bin/\\$_t "\\$pkgdir/usr/bin/\\$_t"
  done
}}
PKGE
cd "$WORK/pkg" && PKGEXT='.pkg.tar' makepkg -f --noconfirm \\
  && ${{ROOTCMD[@]}} pacman -U --overwrite='*' --noconfirm ./*.pkg.tar*
echo "   package: $(pacman -Q {PKGNAME} 2>/dev/null || echo 'not installed')"
'''

REGISTER = f'''
echo "▸ Desktop, symlink and MIME registration"
${{ROOTCMD[@]}} install -d /usr/bin
for _t in wine wineserver winecfg wineboot wineconsole winedbg winefile \\
         winepath winemine regedit regsvr32 msiexec msidb notepad \\
         winebuild winegcc wineg++ winecpp winemaker winedump widl wmc wrc; do
  if [[ -x "{WINE_ROOT}/bin/$_t" && ! -e "/usr/bin/$_t" ]]; then
    ${{ROOTCMD[@]}} ln -sf "{WINE_ROOT}/bin/$_t" "/usr/bin/$_t"
  fi
done
if [[ ! -f {WINE_DESKTOP} ]]; then
  ${{ROOTCMD[@]}} tee {WINE_DESKTOP} >/dev/null <<'DESK'
[Desktop Entry]
Type=Application
Name=Wine Windows Program Loader
Name[tr]=Wine - Windows programı yükleyicisi
Exec={WINE_BIN} start /unix %f
MimeType=application/x-ms-dos-executable;application/x-msi;application/x-ms-shortcut;application/x-bat;application/x-mswinurl
Icon=wine
NoDisplay=true
DESK
fi
xdg-mime default wine.desktop application/x-ms-dos-executable \\
  application/x-msi application/x-ms-shortcut application/x-bat 2>/dev/null || true
${{ROOTCMD[@]}} update-desktop-database /usr/share/applications 2>/dev/null || true
echo "   default .exe handler -> wine.desktop"
'''

QUICK_REPAIR_SCRIPT = f'''
set -uo pipefail
if sudo -n true 2>/dev/null; then ROOTCMD=(sudo); elif command -v pkexec >/dev/null; then ROOTCMD=(pkexec); else ROOTCMD=(sudo); fi
{REGISTER}
echo "Done."
'''

BUILD = f'''
set -uo pipefail
WORK="{WORK}"; mkdir -p "$WORK"
if sudo -n true 2>/dev/null; then ROOTCMD=(sudo); elif command -v pkexec >/dev/null; then ROOTCMD=(pkexec); else ROOTCMD=(sudo); fi
echo "▸ 1/5  Compatible mingw headers and dependencies"
MINGWV=$(pacman -Q mingw-w64-headers 2>/dev/null | cut -d' ' -f2 || true)
if [ "$MINGWV" != "13.0.0-1" ]; then
  echo "   Pinning mingw-w64 headers to 13.0.0"
  mkdir -p "$WORK/mingw13"
  for _p in mingw-w64-headers mingw-w64-crt mingw-w64-winpthreads; do
    _u="https://archive.archlinux.org/packages/m/$(echo $_p | cut -c1)/$_p/$_p-13.0.0-1-any.pkg.tar.zst"
    [ -s "$WORK/mingw13/$_p-13.0.0-1-any.pkg.tar.zst" ] || \\
      curl -fL -o "$WORK/mingw13/$_p-13.0.0-1-any.pkg.tar.zst" "$_u"
  done
  ${{ROOTCMD[@]}} pacman -U --noconfirm "$WORK/mingw13/"*.pkg.tar.zst
else
  echo "   mingw-w64 already compatible (13.0.0)"
fi
echo "▸ 1b/5  Build, ccache, winetricks and Vulkan dependencies"
${{ROOTCMD[@]}} pacman -S --needed --noconfirm base-devel mingw-w64-gcc ccache winetricks cabextract unzip p7zip \\
  vulkan-headers vulkan-icd-loader lib32-vulkan-icd-loader gnutls mesa libglvnd \\
  libx11 libxext libxrandr libxinerama libxcursor libxi freetype2 fontconfig \\
  alsa-lib libpulse libxcomposite libxfixes libxrender

export CC="ccache gcc"
export CXX="ccache g++"
export CROSSCC_x86_64="ccache x86_64-w64-mingw32-gcc"
export CROSSCC_i386="ccache i686-w64-mingw32-gcc"
ccache -M 10G >/dev/null 2>&1 || true

echo "▸ 2/5  Downloading sources"
[[ -s "$WORK/wine-{PKGVER}.tar.xz" ]] || curl -fL -o "$WORK/wine-{PKGVER}.tar.xz" "{WINE_SRC_URL}"
rm -rf "$WORK/wine-{PKGVER}"; tar -xf "$WORK/wine-{PKGVER}.tar.xz" -C "$WORK"
echo "▸ 3/5  Applying patch"
python3 - "$WORK/wine-{PKGVER}/dlls/win32u/vulkan.c" <<'PATCHEOF'
{PATCH_PY}PATCHEOF
[[ $? -eq 0 ]] || {{ echo "!! patch failed"; exit 1; }}
echo "▸ 4/5  Building ($(nproc) cores + ccache)"
rm -rf "$WORK/build" "$WORK/dest"; mkdir -p "$WORK/build" "$WORK/dest"
cd "$WORK/build" && "$WORK/wine-{PKGVER}/configure" --prefix={WINE_ROOT} \\
   --enable-archs=x86_64,i386 --disable-tests >/dev/null \\
&& make -j"$(nproc)" >/dev/null \\
&& make DESTDIR="$WORK/dest" install >/dev/null || {{ echo "!! build failed"; exit 1; }}
echo "▸ 5/5  Creating and installing pacman package"
{PKG_MAKE}
'''

REPAIR_SCRIPT = BUILD + REGISTER + '''
echo
echo "Done."
'''

REBUILD_SCRIPT = BUILD + '''
echo "Done."
'''

UPDATE_SCRIPT = f'''
echo "════════════════════════════════════════════════"
echo "  Update Check"
echo "════════════════════════════════════════════════"
echo
echo "  Installed package : {PKGNAME} {PKGVER}"
echo "  Installed Wine  : $({WINE_BIN} --version 2>/dev/null || echo 'none')"
echo "  32-bit modules : $(ls {WINE_ROOT}/lib/wine/i386-windows/*.dll 2>/dev/null | wc -l)"
echo "  64-bit modules : $(ls {WINE_ROOT}/lib/wine/x86_64-windows/*.dll 2>/dev/null | wc -l)"
echo
echo "▸ Upstream (dl.winehq.org) 11.x releases:"
curl -fsSL "https://dl.winehq.org/wine/source/11.x/" 2>/dev/null \\
  | grep -oE 'wine-[0-9]+\\.[0-9]+(\\.[0-9]+)?\\.tar\\.xz' \\
  | sed 's/\\.tar\\.xz//' | sort -uV | tail -8 | sed 's/^/     /' \\
  || echo "     (list unavailable - check internet connection)"
'''

UNINSTALL_SCRIPT = f'''
set -u
if sudo -n true 2>/dev/null; then ROOTCMD=(sudo); elif command -v pkexec >/dev/null; then ROOTCMD=(pkexec); else ROOTCMD=(sudo); fi
echo "▸ Uninstall starting"
${{ROOTCMD[@]}} pacman -Rdd --noconfirm {PKGNAME} 2>&1 || true
${{ROOTCMD[@]}} rm -rf {WINE_ROOT}
${{ROOTCMD[@]}} rm -f {WINE_DESKTOP}
for f in wine wineserver winecfg wineboot wineconsole winedbg winefile winepath \\
         winemine regedit regsvr32 msiexec msidb notepad winebuild winegcc wineg++ \\
         winecpp winemaker winedump widl wmc wrc; do
  ${{ROOTCMD[@]}} rm -f "/usr/bin/$f" "/usr/local/bin/$f"
done
${{ROOTCMD[@]}} update-desktop-database /usr/share/applications 2>/dev/null || true
rm -rf "{WINE_PROGS_DIR}"
rm -f "{PANEL_DESKTOP}"
rm -f "{ICON_PNG_DIR}"/substance-3d-*.png "{ICON_PNG_DIR}"/adobe-substance-*.png "{ICON_PNG_DIR}"/adobe-wine-panel*.png
rm -f "{ICON_SVG_DIR}"/substance-3d-*.svg "{ICON_SVG_DIR}"/adobe-substance-*.svg "{ICON_SVG_DIR}"/adobe-wine-panel*.svg
rm -f "{PIXMAPS_DIR}"/substance-3d-*.png "{PIXMAPS_DIR}"/adobe-substance-*.png "{PIXMAPS_DIR}"/adobe-wine-panel*.png
update-desktop-database "{LOCAL_APPS_DIR}" 2>/dev/null || true
rm -rf "{WORK}"
echo
echo "  Removed."
'''

# ------------------------------------------------------------------ entrypoint
def main():
    os.makedirs(WORK, exist_ok=True)
    app = QApplication(sys.argv)
    app.setApplicationName("Adobe Wine Panel")
    f = app.font()
    f.setPointSize(10)
    app.setFont(f)
    win = Panel()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
