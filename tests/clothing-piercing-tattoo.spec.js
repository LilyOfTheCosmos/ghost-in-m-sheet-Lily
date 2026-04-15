const { test, expect } = require('@playwright/test');
const { openGame, resetGame, goToPassage, getVar, setVar } = require('./helpers');

test.describe('Clothing — Purchase and Beauty', () => {
  let page;

  test.beforeAll(async ({ browser }) => {
    page = await openGame(browser);
  });

  test.afterAll(async () => {
    await page.close();
  });

  test.beforeEach(async () => {
    await resetGame(page);
    await setVar(page, 'hours', 12);
  });

  test('purchasing jeans1 deducts $30 and sets state to "not worn"', async () => {
    await setVar(page, 'mc.money', 200);
    const startBeauty = await getVar(page, 'mc.beauty');
    await goToPassage(page, 'clothingSection');
    const buyLink = page.locator('.buyItemLink a').first();

    await buyLink.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'clothingSection');

    expect(await getVar(page, 'mc.money')).toBe(200 - 30);
    expect(await getVar(page, 'jeansState1')).toBe('not worn');
    // clothing beauty is applied when wearing, not at purchase
    expect(await getVar(page, 'mc.beauty')).toBe(startBeauty);
  });

  test('purchasing tshirt1 deducts $30 and sets state to "not worn"', async () => {
    await setVar(page, 'mc.money', 500);
    // mark bottom items as already purchased so tshirt1 is the first buy link
    await setVar(page, 'jeansState1', 'not worn');
    await setVar(page, 'jeansState2', 'not worn');
    await setVar(page, 'jeansState3', 'not worn');
    await setVar(page, 'shortsState1', 'not worn');
    await setVar(page, 'shortsState2', 'not worn');
    await setVar(page, 'shortsState3', 'not worn');
    await setVar(page, 'skirtState1', 'not worn');
    await setVar(page, 'skirtState2', 'not worn');
    await setVar(page, 'skirtState3', 'not worn');

    await goToPassage(page, 'clothingSection');
    const buyLink = page.locator('.buyItemLink a').first();

    await buyLink.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'clothingSection');

    expect(await getVar(page, 'mc.money')).toBe(500 - 30);
    expect(await getVar(page, 'tshirtState1')).toBe('not worn');
  });

  test('cannot purchase clothing when money is insufficient', async () => {
    await setVar(page, 'mc.money', 5);
    await goToPassage(page, 'clothingSection');

    const buyLinks = page.locator('.buyItemLink a');
    await expect(buyLinks).toHaveCount(0);
    expect(await getVar(page, 'mc.money')).toBe(5);
  });

  test('already-purchased clothing does not show buy button', async () => {
    await setVar(page, 'mc.money', 1000);
    await setVar(page, 'jeansState1', 'not worn');

    await goToPassage(page, 'clothingSection');
    const buyLinks = page.locator('.buyItemLink a');
    const count = await buyLinks.count();
    // with jeans1 already bought, count should be one less than the full set
    expect(count).toBeLessThan(22);
  });

  test('wearing jeans1 in wardrobe adds +5 beauty', async () => {
    await setVar(page, 'jeansState1', 'not worn');
    await setVar(page, 'jeansState0', 'not worn');
    await setVar(page, 'rememberBottomOuter', 'nojeans0');
    const startBeauty = await getVar(page, 'mc.beauty');

    await goToPassage(page, 'wardrobe');

    // select the jeans1 link specifically by image
    const jeans1Link = page.locator('#availableOuterwear a', {
      has: page.locator('img[src*="jeans1"]'),
    });
    await jeans1Link.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'wardrobe');

    expect(await getVar(page, 'jeansState1')).toBe('worn');
    expect(await getVar(page, 'mc.beauty')).toBe(startBeauty + 5);
  });

  test('wearing bra1 in wardrobe adds +2 beauty', async () => {
    await setVar(page, 'braState1', 'not worn');
    await setVar(page, 'braState0', 'not worn');
    await setVar(page, 'rememberTopUnder', 'nobra0');
    const startBeauty = await getVar(page, 'mc.beauty');

    await goToPassage(page, 'wardrobe');

    // select the bra1 (slip2) link specifically
    const bra1Link = page.locator('#availableClothes a', {
      has: page.locator('img[src*="slip2"]'),
    });
    await bra1Link.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'wardrobe');

    expect(await getVar(page, 'braState1')).toBe('worn');
    expect(await getVar(page, 'mc.beauty')).toBe(startBeauty + 2);
  });

  test('switching from jeans1 (+5) to jeans2 (+8) nets +3 beauty', async () => {
    await setVar(page, 'jeansState0', 'not worn');
    await setVar(page, 'jeansState1', 'worn');
    await setVar(page, 'jeansState2', 'not worn');
    await setVar(page, 'rememberBottomOuter', 'jeans1');
    await setVar(page, 'mc.beauty', 35); // 30 base + 5 from jeans1

    await goToPassage(page, 'wardrobe');

    const jeans2Link = page.locator('#availableOuterwear a', {
      has: page.locator('img[src*="jeans2"]'),
    });
    await jeans2Link.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'wardrobe');

    expect(await getVar(page, 'jeansState2')).toBe('worn');
    expect(await getVar(page, 'jeansState1')).toBe('not worn');
    // +8 new - 5 old = net +3
    expect(await getVar(page, 'mc.beauty')).toBe(35 + 8 - 5);
  });
});

test.describe('Piercing — Purchase and Beauty', () => {
  let page;

  test.beforeAll(async ({ browser }) => {
    page = await openGame(browser);
  });

  test.afterAll(async () => {
    await page.close();
  });

  test.beforeEach(async () => {
    await resetGame(page);
    await setVar(page, 'hours', 12);
  });

  test('purchasing ears piercing adds +2 beauty at purchase', async () => {
    await setVar(page, 'mc.money', 200);
    await goToPassage(page, 'BeautySalonPiercing');
    const buyLink = page.locator('.buyItemLink a').first();

    await buyLink.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'BeautySalonPiercing');

    expect(await getVar(page, 'mc.money')).toBe(200 - 50);
    expect(await getVar(page, 'earsPiercing')).toBe('worn');
    expect(await getVar(page, 'mc.beauty')).toBe(30 + 2);
  });

  test('purchasing nose piercing adds +3 beauty at purchase', async () => {
    await setVar(page, 'mc.money', 200);
    await goToPassage(page, 'BeautySalonPiercing');
    const buyLink = page.locator('.buyItemLink a').nth(1);

    await buyLink.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'BeautySalonPiercing');

    expect(await getVar(page, 'mc.money')).toBe(200 - 70);
    expect(await getVar(page, 'nosePiercing')).toBe('worn');
    expect(await getVar(page, 'mc.beauty')).toBe(30 + 3);
  });

  test('purchasing tongue piercing sets sensitivity modifier, no beauty', async () => {
    await setVar(page, 'mc.money', 200);
    const startBeauty = await getVar(page, 'mc.beauty');
    await goToPassage(page, 'BeautySalonPiercing');
    const buyLink = page.locator('.buyItemLink a').nth(2);

    await buyLink.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'BeautySalonPiercing');

    expect(await getVar(page, 'mc.money')).toBe(200 - 100);
    expect(await getVar(page, 'tonguePiercing')).toBe('worn');
    expect(await getVar(page, 'piercingTongueAddSens')).toBe(0.1);
    // tongue piercing gives sensitivity, not beauty
    expect(await getVar(page, 'mc.beauty')).toBe(startBeauty);
  });

  test('removing ears piercing in wardrobe subtracts beauty', async () => {
    await setVar(page, 'earsPiercing', 'worn');
    await setVar(page, 'mc.beauty', 32); // 30 base + 2 from ears

    await goToPassage(page, 'wardrobe');

    const earsPiercingLink = page.locator('#currentPiercingEars a');
    await earsPiercingLink.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'wardrobe');

    expect(await getVar(page, 'earsPiercing')).toBe('not worn');
    expect(await getVar(page, 'mc.beauty')).toBe(30);
  });

  test('re-wearing ears piercing in wardrobe adds beauty back', async () => {
    await setVar(page, 'earsPiercing', 'not worn');
    await setVar(page, 'mc.beauty', 30);

    await goToPassage(page, 'wardrobe');

    const earsPiercingLink = page.locator('#availablePiercing a').first();
    await earsPiercingLink.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'wardrobe');

    expect(await getVar(page, 'earsPiercing')).toBe('worn');
    expect(await getVar(page, 'mc.beauty')).toBe(32);
  });

  test('removing tongue piercing clears sensitivity modifier', async () => {
    await setVar(page, 'tonguePiercing', 'worn');
    await setVar(page, 'piercingTongueAddSens', 0.1);

    await goToPassage(page, 'wardrobe');

    const tonguePiercingLink = page.locator('#currentPiercingTongue a');
    await tonguePiercingLink.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'wardrobe');

    expect(await getVar(page, 'tonguePiercing')).toBe('not worn');
    expect(await getVar(page, 'piercingTongueAddSens')).toBe(0);
  });
});

test.describe('Tattoo — Purchase and Beauty', () => {
  let page;

  test.beforeAll(async ({ browser }) => {
    page = await openGame(browser);
  });

  test.afterAll(async () => {
    await page.close();
  });

  test.beforeEach(async () => {
    await resetGame(page);
    await setVar(page, 'hours', 12);
  });

  test('purchasing face tattoo deducts $100 and adds +2 beauty', async () => {
    await setVar(page, 'mc.money', 500);
    await goToPassage(page, 'BeautySalonTattoos');
    const buyLink = page.locator('.buyItemLink a').first();

    await buyLink.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'BeautySalonTattoos');

    expect(await getVar(page, 'mc.money')).toBe(500 - 100);
    expect(await getVar(page, 'tattooFace')).toBe('worn');
    expect(await getVar(page, 'mc.beauty')).toBe(30 + 2);
  });

  test('purchasing neck tattoo deducts $80 and adds +2 beauty', async () => {
    await setVar(page, 'mc.money', 500);
    await goToPassage(page, 'BeautySalonTattoos');
    const buyLink = page.locator('.buyItemLink a').nth(1);

    await buyLink.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'BeautySalonTattoos');

    expect(await getVar(page, 'mc.money')).toBe(500 - 80);
    expect(await getVar(page, 'tattooNeck')).toBe('worn');
    expect(await getVar(page, 'mc.beauty')).toBe(30 + 2);
  });

  test('purchasing hand tattoo deducts $50 and adds +1 beauty', async () => {
    await setVar(page, 'mc.money', 500);
    await goToPassage(page, 'BeautySalonTattoos');
    const buyLink = page.locator('.buyItemLink a').nth(2);

    await buyLink.click();
    await page.waitForFunction(() => SugarCube.State.passage === 'BeautySalonTattoos');

    expect(await getVar(page, 'mc.money')).toBe(500 - 50);
    expect(await getVar(page, 'tattooHand')).toBe('worn');
    expect(await getVar(page, 'mc.beauty')).toBe(30 + 1);
  });

  test('corruption-gated tattoo hidden when corruption too low', async () => {
    await setVar(page, 'mc.money', 1000);
    await setVar(page, 'mc.corruption', 2);
    await goToPassage(page, 'BeautySalonTattoos');

    // only 3 regular tattoos should have buy links
    const buyLinks = page.locator('.buyItemLink a');
    await expect(buyLinks).toHaveCount(3);
  });

  test('corruption-gated chest tattoo purchasable at corruption >= 5', async () => {
    await setVar(page, 'mc.money', 1000);
    await setVar(page, 'mc.corruption', 5);

    await goToPassage(page, 'BeautySalonTattoos');

    // with corruption >= 5, all 6 tattoos should show buy links
    const buyLinks = page.locator('.buyItemLink a');
    await expect(buyLinks).toHaveCount(6);

    // buy the chest tattoo (4th buy link = index 3)
    await buyLinks.nth(3).click();
    await page.waitForFunction(() => SugarCube.State.passage === 'BeautySalonTattoos');

    expect(await getVar(page, 'mc.money')).toBe(1000 - 150);
    expect(await getVar(page, 'tattooChest')).toBe('worn');
    expect(await getVar(page, 'mc.beauty')).toBe(30 + 3);
  });

  test('cannot purchase tattoo when money is insufficient', async () => {
    await setVar(page, 'mc.money', 10);
    await goToPassage(page, 'BeautySalonTattoos');

    const buyLinks = page.locator('.buyItemLink a');
    await expect(buyLinks).toHaveCount(0);
    expect(await getVar(page, 'mc.money')).toBe(10);
  });

  test('already-purchased tattoo does not appear again', async () => {
    await setVar(page, 'mc.money', 1000);
    await setVar(page, 'tattooFace', 'worn');
    await goToPassage(page, 'BeautySalonTattoos');

    const buyLinks = page.locator('.buyItemLink a');
    await expect(buyLinks).toHaveCount(2);
  });

  test('buying multiple tattoos accumulates beauty', async () => {
    await setVar(page, 'mc.money', 1000);
    const startBeauty = await getVar(page, 'mc.beauty');

    // buy face tattoo (+2)
    await goToPassage(page, 'BeautySalonTattoos');
    await page.locator('.buyItemLink a').first().click();
    await page.waitForFunction(() => SugarCube.State.passage === 'BeautySalonTattoos');

    // buy neck tattoo (+2) — now the first available
    await page.locator('.buyItemLink a').first().click();
    await page.waitForFunction(() => SugarCube.State.passage === 'BeautySalonTattoos');

    // buy hand tattoo (+1) — now the first available
    await page.locator('.buyItemLink a').first().click();
    await page.waitForFunction(() => SugarCube.State.passage === 'BeautySalonTattoos');

    expect(await getVar(page, 'mc.beauty')).toBe(startBeauty + 2 + 2 + 1);
    expect(await getVar(page, 'mc.money')).toBe(1000 - 100 - 80 - 50);
  });
});
