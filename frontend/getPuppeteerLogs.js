const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
    page.on('requestfailed', request => console.log('REQUEST FAILED:', request.url(), request.failure().errorText));

    try {
        const response = await page.goto('http://localhost:3000', { waitUntil: 'networkidle0' });
        console.log('STATUS:', response.status());
    } catch (err) {
        console.log('NAVIGATION ERROR:', err.message);
    }

    await browser.close();
})();
