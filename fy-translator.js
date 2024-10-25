const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

async function translateText(query, fromLang, toLang) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    await page.goto(`https://fanyi.baidu.com`, { waitUntil: 'networkidle2' });

    // 设置源语言和目标语言，输入内容
    await page.type('#baidu_translate_input', query);
    await page.click(`#transSelectFrom li[data-lang="${fromLang}"]`);
    await page.click(`#transSelectTo li[data-lang="${toLang}"]`);

    // 等待翻译完成
    await page.waitForSelector('.output-bd', { visible: true });
    const result = await page.$eval('.output-bd', el => el.innerText);

    await browser.close();
    return result;
}

// 批量翻译函数
async function batchTranslate(filePath, fromLang, toLang) {
    const outputFilePath = `${path.basename(filePath, '.txt')}-${toLang}.txt`;
    try {
        const data = fs.readFileSync(filePath, 'utf8');
        const lines = data.split('\n');
        const translatedLines = [];

        for (const line of lines) {
            if (line.trim()) {
                const translatedLine = await translateText(line, fromLang, toLang);
                translatedLines.push(translatedLine);
            } else {
                translatedLines.push('');  // 保留空行
            }
        }

        fs.writeFileSync(outputFilePath, translatedLines.join('\n'), 'utf8');
        console.log(`Translation complete! Saved to ${outputFilePath}`);
    } catch (err) {
        console.error('Error during batch translation:', err);
    }
}

// 获取文件路径和翻译选项
const filePath = process.argv[2];  // 从命令行参数传入文件路径
const fromLang = 'zh';
const toLang = 'en';

batchTranslate(filePath, fromLang, toLang);
