const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const REPO_ROOT = path.join(__dirname, '..');
const ASSET_DIRS = ['assets', 'asset-placeholders'];

/**
 * Normalize a single path component (filename or directory name) to the
 * canonical lower kebab-case form used across the repo:
 *   - camelCase / PascalCase boundaries become dashes
 *   - underscores become dashes
 *   - everything is lowercased
 *   - a dash immediately preceding a trailing numeric suffix is dropped
 *     (so `image-name2.png`, not `image-name-2.png`)
 *   - consecutive dashes collapse; leading/trailing dashes trim
 */
function toKebab(name) {
  let stem, ext;
  const dot = name.lastIndexOf('.');
  if (dot >= 0) {
    stem = name.slice(0, dot);
    ext = name.slice(dot).toLowerCase();
  } else {
    stem = name;
    ext = '';
  }
  stem = stem.replace(/([a-z0-9])([A-Z])/g, '$1-$2');
  stem = stem.replace(/([A-Z]+)([A-Z][a-z])/g, '$1-$2');
  stem = stem.replace(/_/g, '-');
  stem = stem.toLowerCase();
  stem = stem.replace(/-(\d+)$/, '$1');
  stem = stem.replace(/-+/g, '-').replace(/^-+|-+$/g, '');
  return stem + ext;
}

// Asset extensions the kebab-case rule applies to. Docs, manifests, and
// other dev metadata at the asset-tree root (README.md, index.json,
// todo.txt, timestamps.txt) are exempt.
const ASSET_EXT_RE = /\.(jpg|jpeg|png|webp|gif|mp4|webm)$/i;

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      out.push({ full, name: entry.name, isDir: true });
      out.push(...walk(full));
    } else if (ASSET_EXT_RE.test(entry.name)) {
      out.push({ full, name: entry.name, isDir: false });
    }
  }
  return out;
}

test.describe('asset filename conventions', () => {

  for (const base of ASSET_DIRS) {
    const baseAbs = path.join(REPO_ROOT, base);
    if (!fs.existsSync(baseAbs)) continue;

    test(`all names under ${base}/ are lower kebab-case with no dashed numeric suffixes`, () => {
      const violations = [];
      for (const { full, name, isDir } of walk(baseAbs)) {
        const expected = toKebab(name);
        if (name !== expected) {
          const rel = path.relative(REPO_ROOT, full);
          violations.push(`${rel}  →  expected "${expected}"`);
        }
      }
      expect(violations, violations.join('\n')).toHaveLength(0);
    });
  }

});
