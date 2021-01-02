const puppeteer = require("puppeteer");
const fs = require("fs").promises;
(async () => {
  const browser = await puppeteer.connect({
    browserWSEndpoint:
      "ws://127.0.0.1:9222/devtools/browser/620208c9-e025-4b33-b943-cc48be2d9fec",
    defaultViewport: null,
  });
  let pages = await browser.pages();
  console.log(
    pages.map((page, i) => {
      return {
        page: page.url(),
        index: i,
      };
    })
  );
  let page = pages[0];
  console.log("在这里开始", page.url());
  while (true) {
    await page.waitFor(1000);
    await page.waitForSelector(".markdown");
    let item = await page.evaluate(async () => {
      let title;
      try {
        title = document.querySelector("h1").innerText;
      } catch {
        title = document.querySelector("h2").innerText;
      }
      let text = document.querySelector(".markdown").innerText;
      return {
        title,
        text,
      };
    });
    await fs.writeFile(`./${item.title}`, item.text);
    let els = await page.$x("//div/a[contains(., '→')]");
    await page.evaluate((el) => {
      el.click();
    }, els[0]);
  }
})();
