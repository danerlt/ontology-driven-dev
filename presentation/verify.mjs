/** 验证观众实际使用的导航、讲解与模拟行为。 */
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const require = createRequire('C:/Users/tao/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/package.json');
const { chromium } = require('playwright');
const root = path.dirname(fileURLToPath(import.meta.url));
const output = path.join(root, 'artifacts');
mkdirSync(output, { recursive: true });
const checks = [];
const check = async (name, run) => {
  try { await run(); checks.push({ name, passed: true }); console.log(`通过：${name}`); }
  catch (error) { checks.push({ name, passed: false, error: error.message }); console.error(`失败：${name}；${error.message}`); }
};
const htmlPath = path.join(root, 'index.html');
await check('独立离线演示文件存在', () => assert.ok(existsSync(htmlPath), '尚未生成演示文件'));
if (!existsSync(htmlPath)) process.exit(1);
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const errors = [];
const requests = [];
page.on('pageerror', e => errors.push(e.message));
page.on('request', r => { if (/^https?:/.test(r.url())) requests.push(r.url()); });
await page.goto(pathToFileURL(htmlPath).href);
await page.evaluate(() => document.fonts.ready);
await check('离线打开且不发起外部资源请求', () => assert.equal(requests.length, 0));
await check('包含十九页完整演示与对应讲解备注', async () => {
  assert.equal(await page.locator('.slide').count(), 19);
  assert.equal(await page.locator('.slide aside.speaker-notes').count(), 19);
});
await check('首尾边界与键盘翻页', async () => {
  await page.keyboard.press('Home'); await page.keyboard.press('ArrowLeft');
  assert.equal(await page.locator('.slide.active').getAttribute('data-slide'), '1');
  await page.keyboard.press('ArrowRight');
  assert.equal(await page.locator('.slide.active').getAttribute('data-slide'), '2');
  await page.keyboard.press('End'); await page.keyboard.press('ArrowRight');
  assert.equal(await page.locator('.slide.active').getAttribute('data-slide'), '19');
});
await check('目录能跳转到指定主题并关闭', async () => {
  await page.getByRole('button', { name: '打开目录', exact: true }).click();
  await page.locator('#outline button[data-go="5"]').click();
  assert.equal(await page.locator('.slide.active').getAttribute('data-slide'), '5');
  assert.equal(await page.locator('#outline').isVisible(), false);
});
await check('七模型交互展示职责与真实 ID', async () => {
  await page.getByRole('button', { name: 'M3 规则模型', exact: true }).click();
  assert.match(await page.locator('#modelDetail').innerText(), /只判断/);
  assert.match(await page.locator('#modelDetail').innerText(), /RULE-CONTRACT-SETTLEMENT/);
});
await check('收款模拟支持结清、冲销恢复、额度拒绝', async () => {
  await page.evaluate(() => window.deck.showSlide(9));
  await page.locator('#receiptAmount').fill('60');
  await page.getByRole('button', { name: '登记模拟收款', exact: true }).click();
  assert.match(await page.locator('#contractState').innerText(), /已结清/);
  await page.getByRole('button', { name: '冲销最近一笔', exact: true }).click();
  assert.match(await page.locator('#contractState').innerText(), /已纳入管理/);
  await page.locator('#receiptAmount').fill('61');
  await page.getByRole('button', { name: '登记模拟收款', exact: true }).click();
  assert.match(await page.locator('#receiptMessage').innerText(), /不得超过/);
  assert.equal(await page.locator('#receivedValue').innerText(), '40');
});
await check('小数收款恰好收齐时不会被浮点误差拒绝', async () => {
  await page.getByRole('button', { name: '重置示例', exact: true }).click();
  for (const amount of ['59.99', '0.01']) {
    await page.locator('#receiptAmount').fill(amount);
    await page.getByRole('button', { name: '登记模拟收款', exact: true }).click();
  }
  assert.equal(await page.locator('#receivedValue').innerText(), '100');
  assert.equal(await page.locator('#contractState').innerText(), '已结清');
});
await check('合同审批在一百万元边界切换总经理节点', async () => {
  await page.evaluate(() => window.deck.showSlide(10));
  await page.locator('#contractAmount').fill('99'); await page.locator('#contractAmount').dispatchEvent('input');
  assert.equal(await page.locator('#gmStep').getAttribute('data-enabled'), 'false');
  await page.locator('#contractAmount').fill('100'); await page.locator('#contractAmount').dispatchEvent('input');
  assert.equal(await page.locator('#gmStep').getAttribute('data-enabled'), 'true');
});
await check('备注展示当前页讲稿与来源', async () => {
  await page.locator('#contractAmount').blur();
  await page.keyboard.press('n');
  assert.equal(await page.locator('#notesPanel').isVisible(), true);
  assert.match(await page.locator('#notesText').innerText(), /100|一百/);
  assert.ok(await page.locator('#notesSources a').count() > 0);
  await page.keyboard.press('Escape');
});
await check('编辑内容可保存并在刷新后恢复', async () => {
  await page.keyboard.press('Home'); await page.keyboard.press('e');
  const editable = page.locator('.slide.active [data-edit]').first();
  await editable.fill('把业务共识变成系统骨架');
  await page.keyboard.press('Control+Enter');
  await page.reload();
  assert.equal(await page.locator('.slide.active [data-edit]').first().innerText(), '把业务共识变成系统骨架');
});
await check('下载后的 HTML 保留修改且可独立打开', async () => {
  const waiting = page.waitForEvent('download');
  await page.getByRole('button', { name: '下载离线 HTML', exact: true }).click();
  const download = await waiting;
  const downloadedPath = path.join(output, 'exported.html');
  await download.saveAs(downloadedPath);
  const exported = await browser.newPage();
  await exported.goto(pathToFileURL(downloadedPath).href);
  assert.equal(await exported.locator('.slide').count(), 19);
  assert.equal(await exported.locator('[data-edit="cover-title"]').innerText(), '把业务共识变成系统骨架');
  assert.equal(await exported.locator('#outlineGrid button').count(), 19);
  await exported.getByRole('button', { name: '打开目录', exact: true }).click();
  await exported.locator('#outline button[data-go="5"]').click();
  assert.equal(await exported.locator('.slide.active').getAttribute('data-slide'), '5');
  assert.equal(await exported.locator('#outline').isVisible(), false);
  await exported.close();
  await page.evaluate(() => localStorage.clear()); await page.reload();
});
await check('编辑后的标题会同步到目录和讲稿且刷新不丢失', async () => {
  await page.evaluate(() => window.deck.showSlide(1));
  await page.keyboard.press('e');
  await page.locator('.slide.active h2[data-edit]').fill('业务语义的一致性');
  await page.keyboard.press('Control+Enter');
  await page.reload();
  assert.match(await page.locator('#outline button[data-go="2"]').innerText(), /业务语义的一致性/);
  await page.keyboard.press('n');
  assert.match(await page.locator('#notesTitle').innerText(), /业务语义的一致性/);
  await page.keyboard.press('Escape');
  await page.evaluate(() => localStorage.clear()); await page.reload();
});
const geometry = [];
await check('桌面与手机上的十九页均保持比例且内容不越界', async () => {
  const issues = [];
  for (const size of [{ width: 1280, height: 720 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(size);
    for (let i = 0; i < 19; i++) {
      await page.evaluate(i => window.deck.showSlide(i), i);
      await page.waitForTimeout(40);
      const result = await page.locator('.slide.active').evaluate(slide => {
        const bounds = slide.getBoundingClientRect();
        const overflow = [];
        for (const el of slide.querySelectorAll('[data-check]')) {
          const r = el.getBoundingClientRect();
          if (r.width > 0 && (r.right > bounds.right + 2 || r.bottom > bounds.bottom + 2 || r.left < bounds.left - 2 || r.top < bounds.top - 2 || el.scrollHeight > el.clientHeight + 3 || el.scrollWidth > el.clientWidth + 3)) overflow.push(el.getAttribute('data-check'));
        }
        return { ratio: bounds.width / bounds.height, overflow };
      });
      geometry.push({ viewport: size, slide: i + 1, ...result });
      assert.ok(Math.abs(result.ratio - 16 / 9) < .001, `第 ${i + 1} 页比例错误`);
      if (result.overflow.length) issues.push(`${size.width} 像素下第 ${i+1} 页：${result.overflow.join('、')}`);
      if (size.width === 1280) await page.screenshot({ path: path.join(output, `slide-${String(i + 1).padStart(2, '0')}.png`) });
    }
    if (size.width === 390) { await page.keyboard.press('Home'); await page.screenshot({ path: path.join(output, 'phone.png') }); }
  }
  assert.deepEqual(issues, [], `发现内容越界：${issues.join('；')}`);
});
await check('打印模式显示全部页面', async () => {
  await page.emulateMedia({ media: 'print' });
  const count = await page.locator('.slide').evaluateAll(slides => slides.filter(s => getComputedStyle(s).visibility === 'visible').length);
  assert.equal(count, 19);
  await page.pdf({ path: path.join(output, 'print-check.pdf'), width: '1920px', height: '1080px', printBackground: true });
});
await check('运行过程无 JavaScript 异常', () => assert.deepEqual(errors, []));
writeFileSync(path.join(output, 'verification.json'), JSON.stringify({ checks, geometry, errors }, null, 2));
await browser.close();
const failed = checks.filter(c => !c.passed).length;
console.log(`校验完成：${checks.length - failed} 项通过，${failed} 项失败。`);
if (failed) process.exitCode = 1;
