import sys, asyncio, pathlib
sys.stdout.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

HTML = pathlib.Path(__file__).parent / "index.html"

async def main():
    results = []
    def chk(name, passed, detail=""):
        mark = "✓" if passed else "✗"
        results.append((passed, name, detail))
        print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        await page.goto(HTML.as_uri())
        await page.wait_for_load_state("networkidle")

        # 1. Basic load
        title = await page.title()
        chk("Page loads", bool(title), title)

        # 2. closeIssueModal defined
        cm_type = await page.evaluate("typeof closeIssueModal")
        chk("closeIssueModal defined", cm_type == "function", cm_type)

        # 3. Drug cards rendered
        cards = await page.query_selector_all(".drug-card")
        chk("Drug cards rendered (>=57)", len(cards) >= 57, f"{len(cards)} cards")

        # 4. Open detail modal via first drug card
        await cards[0].click()
        await page.wait_for_timeout(400)
        det_open = await page.evaluate("document.getElementById('detModal')?.classList.contains('open')")
        chk("Detail modal opens on card click", det_open)

        # 5. Find and click 通報問題 button (use JS click to bypass overlay pointer interception)
        has_report_btn = await page.evaluate(
            "!!document.querySelector(\"[onclick*='openIssueReporter']\")"
        )
        chk("通報問題 button found in detail modal", has_report_btn)
        if has_report_btn:
            await page.evaluate("document.querySelector(\"[onclick*='openIssueReporter']\").click()")
            await page.wait_for_timeout(400)
            issue_open = await page.evaluate("document.getElementById('issueModal')?.classList.contains('open')")
            chk("Issue modal opens", issue_open)

            # 6. X button closes modal
            has_x = await page.evaluate("!!document.querySelector('#issueC .modal-close')")
            chk("X button found in issue modal", has_x)
            if has_x:
                await page.evaluate("document.querySelector('#issueC .modal-close').click()")
                await page.wait_for_timeout(300)
                issue_closed = not await page.evaluate("document.getElementById('issueModal')?.classList.contains('open')")
                chk("X button closes issue modal", issue_closed)

            # 7. Re-open and test Cancel button
            await page.evaluate("document.querySelector(\"[onclick*='openIssueReporter']\").click()")
            await page.wait_for_timeout(300)
            has_cancel = await page.evaluate("!!document.querySelector('#issueC .ghost-btn')")
            chk("Cancel button found in issue modal", has_cancel)
            if has_cancel:
                await page.evaluate("document.querySelector('#issueC .ghost-btn').click()")
                await page.wait_for_timeout(300)
                issue_closed2 = not await page.evaluate("document.getElementById('issueModal')?.classList.contains('open')")
                chk("Cancel button closes issue modal", issue_closed2)

        # 8. No JS errors on load
        chk("No JS errors on load", len(errors) == 0, "; ".join(errors) if errors else "clean")

        # 9. Admin panel collapsed by default
        admin_collapsed = await page.evaluate(
            "document.querySelector('.admin-panel.is-collapsed') !== null"
        )
        chk("Admin panel collapsed by default", admin_collapsed)

        # 10. Subtitle mentions 57 drugs
        subtitle = await page.inner_text(".header-sub")
        chk("Subtitle mentions 57 drugs", "57" in subtitle, subtitle.strip())

        await browser.close()

    passed = sum(1 for r in results if r[0])
    total = len(results)
    print(f"\n{'='*40}")
    print(f"Result: {passed}/{total} passed")
    if passed < total:
        print("FAILED checks:")
        for ok, name, detail in results:
            if not ok:
                print(f"  ✗ {name}" + (f" — {detail}" if detail else ""))
    return 0 if passed == total else 1

sys.exit(asyncio.run(main()))
