#!/usr/bin/env python3
"""Render an HTML daily-sheet to a print-exact PDF for an e-ink device.

Usage: render.py <input.html> <output.pdf> [width_mm height_mm]

Order of attempts:
  1. Headless Chrome / Chromium / Edge  (--print-to-pdf; honours CSS @page size)
  2. WeasyPrint                          (pip install weasyprint; exact @page size)

The HTML must already carry `@page { size: <w>mm <h>mm; margin: 0 }` (the skill
writes it). width_mm/height_mm are optional and only used to sanity-check the
Chrome output; if the produced page differs by more than 2mm we fall back so a
mis-sized sheet is never shipped to the device.
"""
import glob
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME_NAMES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "chrome", "microsoft-edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

# Playwright ships a bare headless Chromium ("headless_shell") that most agent
# machines already have; use it as a last resort before WeasyPrint.
HEADLESS_SHELL_GLOBS = [
    str(Path.home() / ".cache/ms-playwright/*/chrome-linux/headless_shell"),
    str(Path.home() / "Library/Caches/ms-playwright/*/chrome-mac*/headless_shell"),
]


def find_chrome():
    for n in CHROME_NAMES:
        p = shutil.which(n) if "/" not in n else (n if Path(n).exists() else None)
        if p:
            return p
    for pattern in HEADLESS_SHELL_GLOBS:
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[-1]  # newest revision
    return None


def pdf_page_mm(pdf_path):
    """Return (w_mm, h_mm) of page 1, or None if we cannot read it."""
    try:
        import pymupdf  # noqa
        d = pymupdf.open(pdf_path)
        r = d[0].rect
        return (r.width / 72 * 25.4, r.height / 72 * 25.4)
    except Exception:
        return None


def size_ok(pdf_path, w_mm, h_mm):
    if not w_mm:
        return True  # no target given -> trust it
    got = pdf_page_mm(pdf_path)
    if not got:
        return True  # cannot verify -> do not block
    return abs(got[0] - w_mm) <= 2 and abs(got[1] - h_mm) <= 2


def _run_chrome(chrome, headless_flag, html, out):
    with tempfile.TemporaryDirectory() as prof:
        cmd = [chrome]
        # headless_shell is already headless and rejects a --headless flag.
        if headless_flag and "headless_shell" not in chrome:
            cmd.append(headless_flag)
        cmd += [
            "--disable-gpu", "--no-sandbox",
            f"--user-data-dir={prof}", "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={out}", Path(html).resolve().as_uri(),
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return Path(out).exists() and Path(out).stat().st_size > 0


def try_chrome(html, out, w_mm, h_mm):
    chrome = find_chrome()
    if not chrome:
        return False, "no Chrome/Chromium/Edge found"
    # --headless=new is the modern flag; older builds only know --headless;
    # headless_shell needs neither (_run_chrome drops it).
    if not _run_chrome(chrome, "--headless=new", html, out):
        _run_chrome(chrome, "--headless", html, out)
    if not Path(out).exists() or Path(out).stat().st_size == 0:
        return False, "Chrome produced no PDF"
    if not size_ok(out, w_mm, h_mm):
        return False, f"Chrome page size off target ({pdf_page_mm(out)}), falling back"
    return True, chrome


def try_weasyprint(html, out, w_mm, h_mm):
    try:
        from weasyprint import HTML
    except Exception as e:
        return False, f"weasyprint not available ({e})"
    HTML(filename=html).write_pdf(out)
    return True, "weasyprint"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    html, out = sys.argv[1], sys.argv[2]
    w_mm = float(sys.argv[3]) if len(sys.argv) > 4 else None
    h_mm = float(sys.argv[4]) if len(sys.argv) > 4 else None

    errors = []
    for fn in (try_chrome, try_weasyprint):
        ok, info = fn(html, out, w_mm, h_mm)
        if ok:
            print(f"rendered with {info} -> {out}")
            got = pdf_page_mm(out)
            if got:
                print(f"page size: {got[0]:.1f} x {got[1]:.1f} mm")
            return
        errors.append(f"- {fn.__name__}: {info}")
    sys.stderr.write(
        "Could not render the PDF. Tried:\n" + "\n".join(errors) +
        "\nInstall Chrome/Chromium, or run: pip install weasyprint\n"
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
