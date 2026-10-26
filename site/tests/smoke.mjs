import assert from 'node:assert/strict'
import { existsSync } from 'node:fs'
import { mkdir } from 'node:fs/promises'
import { chromium } from '@playwright/test'

const url = process.env.SITE_URL || 'http://127.0.0.1:5173'
const macChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const executablePath = process.env.CHROME_PATH || (existsSync(macChrome) ? macChrome : undefined)
const browser = await chromium.launch({ executablePath, headless: true, args: ['--enable-unsafe-swiftshader'] })
const resultsDir = new URL('../test-results/', import.meta.url).pathname
await mkdir(resultsDir, { recursive: true })
const errors = []

try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  const page = await context.newPage()
  page.on('pageerror', error => errors.push(error.message))
  await page.goto(url)
  await page.locator('.sphere-canvas.is-ready').waitFor()
  assert.equal((await page.locator('body').innerText()).trim(), '', 'The page has no visible text')
  assert.equal(await page.locator('button, a').count(), 0, 'The scene has no controls or links')
  const plant = page.locator('.plant').first()
  const cloud = page.locator('.cloud').first()
  const movingPlant = await plant.evaluate(el => getComputedStyle(el).transform)
  const movingCloud = await cloud.evaluate(el => getComputedStyle(el).translate)
  await page.waitForTimeout(250)
  assert.notEqual(await plant.evaluate(el => getComputedStyle(el).transform), movingPlant, 'Plants move with the wind')
  assert.notEqual(await cloud.evaluate(el => getComputedStyle(el).translate), movingCloud, 'Clouds drift behind the character')
  for (const width of [1440, 390, 768]) {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 })
    await page.waitForTimeout(150)
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth || document.documentElement.scrollHeight > window.innerHeight)
    assert.equal(overflow, false, `Scene fits the viewport at ${width}px`)
    if (width !== 768) await page.screenshot({ path: `${resultsDir}/hero-${width === 390 ? 'mobile' : 'desktop'}.png`, animations: 'disabled' })
  }
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.waitForTimeout(100)
  assert.equal(await plant.evaluate(el => getComputedStyle(el).animationName), 'none', 'System motion preference stops the wind')
  assert.equal(await cloud.evaluate(el => getComputedStyle(el).animationName), 'none', 'System motion preference stops the clouds')
  await context.close()

  const fallback = await browser.newContext()
  const fallbackPage = await fallback.newPage()
  await fallbackPage.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext
    HTMLCanvasElement.prototype.getContext = function (type, ...args) {
      if (type.includes('webgl')) return null
      return original.call(this, type, ...args)
    }
  })
  await fallbackPage.goto(url)
  await fallbackPage.locator('.sphere-canvas').waitFor({ state: 'attached' })
  assert.equal(await fallbackPage.locator('.sphere-fallback').isVisible(), true, 'Smiling SVG remains visible without WebGL')
  await fallback.close()
  assert.deepEqual(errors, [], 'No browser runtime errors')
  console.log('Passed: no visible text or controls, WebGL sphere, wind, clouds, 390/768/1440 layouts, reduced motion, and WebGL fallback.')
  console.log(`Screenshots: ${resultsDir}`)
} finally {
  await browser.close()
}
