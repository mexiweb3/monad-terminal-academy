"""
Genera screenshots para el pitch (iteración 2):
- landing desktop + mobile
- webclient: login, home, ls+cat, quests, claim
- webclient flujo intermedio: pipe_dojo, redirect_dojo
- webclient flujo Claude: claude_dojo banner, skills list, new contract, deploy

Uso: source ../.venv/bin/activate && python _take_screenshots.py
"""
from pathlib import Path
import asyncio
import sys
import time as _time

from playwright.async_api import async_playwright

LANDING_URL = "https://aka-warning-old-geneva.trycloudflare.com/"
WEB_URL = "https://die-hand-alexandria-joan.trycloudflare.com/webclient/"
TEST_WALLET = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

OUT = Path(__file__).parent / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


async def landing(pw):
    browser = await pw.chromium.launch()

    ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
    page = await ctx.new_page()
    await page.goto(LANDING_URL, wait_until="networkidle", timeout=30_000)
    await page.wait_for_timeout(600)
    await page.screenshot(path=str(OUT / "landing-desktop.png"), full_page=True)
    print("✓ landing-desktop.png")
    await ctx.close()

    ctx = await browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    page = await ctx.new_page()
    await page.goto(LANDING_URL, wait_until="networkidle", timeout=30_000)
    await page.wait_for_timeout(600)
    await page.screenshot(path=str(OUT / "landing-mobile.png"), full_page=True)
    print("✓ landing-mobile.png")
    await ctx.close()

    await browser.close()


async def send_cmd(page, cmd: str, wait_ms: int = 1200):
    """Evennia monta el textarea con class="inputfield" (no id) tras cargar el JS del cliente."""
    await page.evaluate("""(text) => {
        const ta = document.querySelector('textarea.inputfield');
        if (!ta) throw new Error('textarea.inputfield no encontrado');
        ta.focus();
        ta.value = text;
    }""", cmd)
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(wait_ms)


async def clear_output(page):
    """Comando 'clear' del juego: limpia el pane de output para dejar el siguiente snapshot legible."""
    await send_cmd(page, "clear", wait_ms=800)


async def webclient(pw):
    browser = await pw.chromium.launch()
    ctx = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await ctx.new_page()

    console_errors = []
    page.on("pageerror", lambda e: console_errors.append(str(e)))

    await page.goto(WEB_URL, wait_until="load", timeout=30_000)
    await page.wait_for_selector("textarea.inputfield", state="attached", timeout=25_000)
    await page.wait_for_timeout(3_000)

    # 01 — Login screen
    await page.screenshot(path=str(OUT / "webclient-01-login.png"), full_page=False)
    print("✓ webclient-01-login.png")

    # Usuario nuevo con sufijo timestamp para evitar colisión entre runs
    uid = f"demo{int(_time.time()) % 100000}"
    pwd = "testpass123!"
    await send_cmd(page, f"create {uid} {pwd}", wait_ms=2500)
    await send_cmd(page, "Y", wait_ms=2000)
    await send_cmd(page, f"connect {uid} {pwd}", wait_ms=3000)
    await send_cmd(page, "look", wait_ms=1500)

    # 02 — Home (academia)
    await page.screenshot(path=str(OUT / "webclient-02-home.png"), full_page=False)
    print(f"✓ webclient-02-home.png (user={uid})")

    # Tier 1: shell básico
    await send_cmd(page, "ls", wait_ms=1200)
    await send_cmd(page, "cat README.txt", wait_ms=1200)
    await send_cmd(page, "pwd", wait_ms=1000)
    await page.screenshot(path=str(OUT / "webclient-03-ls-cat.png"), full_page=False)
    print("✓ webclient-03-ls-cat.png")

    # Navegar por las rooms: ls → cd → cat → mkdir (completa Tier 1 quests)
    await send_cmd(page, "cd ls_dojo", wait_ms=1000)
    await send_cmd(page, "cd cd_dojo", wait_ms=1000)
    await send_cmd(page, "cd cat_dojo", wait_ms=1000)
    await send_cmd(page, "cd mkdir_dojo", wait_ms=1000)
    await send_cmd(page, "touch demo.txt", wait_ms=1000)
    await send_cmd(page, "mkdir demodir", wait_ms=1000)
    await send_cmd(page, "grep Monad README.txt", wait_ms=1200)

    # Tier 2: shell intermedio — echo/whoami/head/tail/wc/man/history
    await send_cmd(page, "whoami", wait_ms=900)
    await send_cmd(page, "echo hola mundo", wait_ms=900)
    await send_cmd(page, "man ls", wait_ms=900)
    await send_cmd(page, "head README.txt", wait_ms=900)
    await send_cmd(page, "tail README.txt", wait_ms=900)
    await send_cmd(page, "wc README.txt", wait_ms=900)
    await send_cmd(page, "history", wait_ms=900)

    # --- pipe_dojo: | operator
    await send_cmd(page, "cd pipe_dojo", wait_ms=1200)
    await clear_output(page)
    await send_cmd(page, "look", wait_ms=1000)
    await send_cmd(page, "echo hola mundo terminal | wc", wait_ms=1500)
    await send_cmd(page, "cat README.txt | wc", wait_ms=1500)
    await page.screenshot(path=str(OUT / "webclient-06-pipe.png"), full_page=False)
    print("✓ webclient-06-pipe.png")

    # --- redirect_dojo: > y >>
    await send_cmd(page, "cd redirect_dojo", wait_ms=1200)
    await clear_output(page)
    await send_cmd(page, "look", wait_ms=1000)
    await send_cmd(page, "echo primera linea > mi.log", wait_ms=1200)
    await send_cmd(page, "echo segunda linea >> mi.log", wait_ms=1200)
    await send_cmd(page, "cat mi.log", wait_ms=1200)
    await page.screenshot(path=str(OUT / "webclient-07-redirect.png"), full_page=False)
    print("✓ webclient-07-redirect.png")

    # --- final_exam + claude_dojo
    await send_cmd(page, "cd final_exam", wait_ms=1200)
    await send_cmd(page, "cd claude_dojo", wait_ms=1500)

    # 08 — `claude` banner + `claude skills list`
    await clear_output(page)
    await send_cmd(page, "claude", wait_ms=1500)
    await send_cmd(page, "claude skills list", wait_ms=1500)
    await page.screenshot(path=str(OUT / "webclient-08-skills.png"), full_page=False)
    print("✓ webclient-08-skills.png")

    # 09 — claude skills install + new contract
    await clear_output(page)
    await send_cmd(page, "claude skills install austin-griffith/monad-kit", wait_ms=1500)
    await send_cmd(page, "claude new contract MiPrimerToken", wait_ms=1500)
    await send_cmd(page, "cat MiPrimerToken.sol", wait_ms=1500)
    await page.screenshot(path=str(OUT / "webclient-09-newcontract.png"), full_page=False)
    print("✓ webclient-09-newcontract.png")

    # 10 — claude deploy (CLÍMAX)
    await clear_output(page)
    await send_cmd(page, "claude deploy MiPrimerToken.sol", wait_ms=3000)
    await page.screenshot(path=str(OUT / "webclient-10-deploy.png"), full_page=False)
    print("✓ webclient-10-deploy.png")

    # 04 — quests panel (tier 3 ya casi completo)
    await clear_output(page)
    await send_cmd(page, "quests", wait_ms=1500)
    await page.screenshot(path=str(OUT / "webclient-04-quests.png"), full_page=False)
    print("✓ webclient-04-quests.png")

    # 05 — link + claim onchain
    await clear_output(page)
    await send_cmd(page, f"link {TEST_WALLET}", wait_ms=1500)
    await send_cmd(page, "claim", wait_ms=15_000)
    await page.screenshot(path=str(OUT / "webclient-05-claim.png"), full_page=False)
    print("✓ webclient-05-claim.png")

    if console_errors:
        print("⚠️ errores en la página:", console_errors[:3])

    await ctx.close()
    await browser.close()


async def main():
    async with async_playwright() as pw:
        print("→ Landing screenshots…")
        await landing(pw)
        print("→ Webclient screenshots…")
        await webclient(pw)
    print("listo")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        raise
