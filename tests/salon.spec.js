const { test, expect } = require('@playwright/test');
const { openGame, resetGame, setVar, callSetup } = require('./helpers');

test.describe('Salon Controller', () => {
  let page;

  test.beforeAll(async ({ browser }) => {
    page = await openGame(browser);
  });

  test.afterAll(async () => {
    await page.close();
  });

  test.beforeEach(async () => {
    await resetGame(page);
  });

  test('isOpen true during operating hours (8-21)', async () => {
    // arrange
    await setVar(page, 'hours', 12);

    // act
    const result = await callSetup(page, 'setup.Salon.isOpen()');

    // assert
    expect(result).toBe(true);
  });

  test('isOpen true at hour 8', async () => {
    // arrange
    await setVar(page, 'hours', 8);

    // act
    const result = await callSetup(page, 'setup.Salon.isOpen()');

    // assert
    expect(result).toBe(true);
  });

  test('isOpen true at hour 21', async () => {
    // arrange
    await setVar(page, 'hours', 21);

    // act
    const result = await callSetup(page, 'setup.Salon.isOpen()');

    // assert
    expect(result).toBe(true);
  });

  test('isOpen false at hour 7 (boundary)', async () => {
    // arrange
    await setVar(page, 'hours', 7);

    // act
    const result = await callSetup(page, 'setup.Salon.isOpen()');

    // assert
    expect(result).toBe(false);
  });

  test('isOpen false at hour 22 (boundary)', async () => {
    // arrange
    await setVar(page, 'hours', 22);

    // act
    const result = await callSetup(page, 'setup.Salon.isOpen()');

    // assert
    expect(result).toBe(false);
  });

  test('isOpen false at midnight', async () => {
    // arrange
    await setVar(page, 'hours', 0);

    // act
    const result = await callSetup(page, 'setup.Salon.isOpen()');

    // assert
    expect(result).toBe(false);
  });
});
