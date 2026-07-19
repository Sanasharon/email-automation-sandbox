const puppeteer = require('puppeteer');

(async () => {
  console.log('Starting puppeteer...');
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  console.log('Navigating to dashboard...');
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: '../dashboard_real_data.png' });

  console.log('Navigating to workflows...');
  await page.goto('http://localhost:5173/workflows', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: '../workflows_real_data.png' });

  console.log('Navigating to monitoring...');
  await page.goto('http://localhost:5173/monitoring', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: '../emails_real_data.png' });

  console.log('Screenshots taken.');
  await browser.close();
})();
