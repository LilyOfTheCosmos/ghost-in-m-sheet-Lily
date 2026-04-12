const path = require('path');

const GAME_URL = `file://${path.resolve(__dirname, '..', 'ghost-in-msheet.html')}`;

/**
 * Wait for SugarCube to finish initializing and rendering a passage.
 */
async function waitForSugarCube(page) {
  await page.waitForFunction(() =>
    typeof SugarCube !== 'undefined' &&
    SugarCube.State &&
    SugarCube.State.variables &&
    SugarCube.Engine
  );
}

/**
 * Navigate to a SugarCube passage by name and wait for it to render.
 */
async function goToPassage(page, passageName) {
  await page.evaluate((p) => SugarCube.Engine.play(p), passageName);
  await page.waitForFunction(
    (p) => SugarCube.State.passage === p,
    passageName
  );
}

/**
 * Read a SugarCube story variable (e.g. "mc.money" → $mc.money).
 */
function getVar(page, varName) {
  return page.evaluate((v) => {
    const parts = v.split('.');
    let value = SugarCube.State.variables;
    for (const p of parts) value = value[p];
    return value;
  }, varName);
}

/**
 * Set a SugarCube story variable.
 */
function setVar(page, varName, value) {
  return page.evaluate(({ v, val }) => {
    const parts = v.split('.');
    let target = SugarCube.State.variables;
    for (let i = 0; i < parts.length - 1; i++) target = target[parts[i]];
    target[parts[parts.length - 1]] = val;
  }, { v: varName, val: value });
}

/**
 * Call a setup.* controller method and return the result.
 */
function callSetup(page, expr) {
  return page.evaluate((e) => {
    return new Function('setup', 'return ' + e)(SugarCube.setup);
  }, expr);
}

/**
 * Open the game and wait for SugarCube. Returns the page.
 */
async function openGame(browser) {
  const page = await browser.newPage();
  await page.goto(GAME_URL, { waitUntil: 'load' });
  await waitForSugarCube(page);
  return page;
}

module.exports = {
  GAME_URL,
  waitForSugarCube,
  goToPassage,
  getVar,
  setVar,
  callSetup,
  openGame,
};
