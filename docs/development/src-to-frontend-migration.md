# src/ to frontend/ Migration Guide

**Status:** 📋 Planning - Not Yet Implemented
**Priority:** Medium
**Estimated Effort:** 2-3 hours
**Last Updated:** 2025-11-23

## Overview

This guide provides step-by-step instructions for renaming the `src/` directory to `frontend/` to match the `backend/` naming convention and improve monorepo clarity.

### Why Rename?

**Current Structure:**
```
ProjectGoat/
├── backend/     # Python/FastAPI
├── src/         # React/TypeScript (unclear naming)
```

**Proposed Structure:**
```
ProjectGoat/
├── backend/     # Python/FastAPI
├── frontend/    # React/TypeScript (clear, consistent)
```

**Benefits:**
- ✅ Consistent naming convention (backend/ + frontend/)
- ✅ Clearer for new contributors
- ✅ Matches FastAPI full-stack template conventions
- ✅ More intuitive for monorepo structure
- ✅ Standard pattern for mature projects

**Drawbacks:**
- ⚠️ Git history shows as deleted/added (but history preserved)
- ⚠️ Multiple config files need updates
- ⚠️ Active development might conflict during migration

---

## Prerequisites

### Before You Begin

1. **Commit all changes:**
   ```bash
   git status  # Ensure clean working tree
   git add .
   git commit -m "Your message"
   ```

2. **Create backup branch:**
   ```bash
   git checkout -b backup-before-frontend-rename
   git checkout main  # or your working branch
   ```

3. **Ensure tests pass:**
   ```bash
   python -m pytest
   npm run test:e2e
   ```

4. **Close development servers:**
   - Stop `npm run dev`
   - Stop `python run.py`

### Required Tools

- Git
- Text editor
- Terminal/Command Prompt

---

## Step 1: Identify All References

Before renaming, identify what references `src/`:

```bash
# Search for src/ references (exclude node_modules)
grep -r "src/" --include="*.json" --include="*.ts" --include="*.js" --exclude-dir=node_modules --exclude-dir=build .

# Specifically check these files:
grep "src" vite.config.ts
grep "src" tsconfig.json
grep "src" package.json
grep "src" .gitignore
grep "src" .prettierignore
```

### Common Files That Reference src/

| File | Typical Reference | Action Needed |
|------|-------------------|---------------|
| `vite.config.ts` | Root path config | Update paths |
| `tsconfig.json` | Include patterns | Update includes |
| `package.json` | Scripts (rare) | Update if present |
| `.gitignore` | Ignore patterns | Update if src-specific |
| `.prettierignore` | Ignore patterns | Update if src-specific |
| `docs/guides/frontend-development.md` | Code examples | Update paths |

---

## Step 2: Rename the Directory

### Execute the Rename

```bash
# Simple rename
mv src frontend

# Verify the rename
ls -la | grep frontend
```

### What Git Will Show

```bash
git status
```

Will show:
```
deleted:    src/
new file:   frontend/
```

**Note:** Git tracks content, not just filenames. The history is preserved.

---

## Step 3: Update Configuration Files

### 3.1 Update vite.config.ts

**Read the file first:**
```bash
cat vite.config.ts
```

**Look for patterns like:**
```typescript
export default defineConfig({
  root: './src',  // ← Change to './frontend'
  // or
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')  // ← Change to './frontend'
    }
  }
})
```

**Make the changes:**
- Replace all `'./src'` with `'./frontend'`
- Replace all `'/src'` with `'/frontend'`
- Replace `'./src/'` with `'./frontend/'`

### 3.2 Update tsconfig.json

**Read the file:**
```bash
cat tsconfig.json
```

**Look for:**
```json
{
  "include": ["src/**/*"],  // ← Change to "frontend/**/*"
  "compilerOptions": {
    "baseUrl": "src",  // ← Change to "frontend" if present
    "paths": {
      "@/*": ["./src/*"]  // ← Change to "./frontend/*" if present
    }
  }
}
```

**Update all references** from `src` to `frontend`.

### 3.3 Update package.json (If Needed)

**Check for scripts:**
```bash
grep "src" package.json
```

**Common patterns:**
```json
{
  "scripts": {
    "format": "prettier --write src/**/*.{ts,tsx}",  // ← Update if present
    "lint": "eslint src"  // ← Update if present
  }
}
```

**If found:** Update `src` to `frontend`.

### 3.4 Update .gitignore (If Needed)

**Check for src-specific patterns:**
```bash
grep "src" .gitignore
```

**If found:** Update patterns like:
```
# Before
src/temp/

# After
frontend/temp/
```

### 3.5 Update .prettierignore (If Needed)

**Check:**
```bash
grep "src" .prettierignore
```

**Update if patterns exist** (unlikely but check).

---

## Step 4: Update Documentation

### Files to Update

**1. docs/guides/frontend-development.md**

Update paths in code examples:
```typescript
// Before
import api from './src/services/api';

// After
import api from './frontend/services/api';
```

**2. .github/CONTRIBUTING.md**

Update project structure:
```
ProjectGoat/
├── backend/              # Python/FastAPI backend
├── frontend/             # React/TypeScript frontend  ← Update this line
├── tests/               # Test files
```

---

## Step 5: Test the Changes

### Critical Testing Checklist

**5.1 TypeScript Compilation**
```bash
npx tsc --noEmit
```
✅ Should complete without errors

**5.2 Development Server**
```bash
npm run dev
```
✅ Should start on http://localhost:3000
✅ No errors in terminal
✅ Open browser and verify app loads
✅ Check browser console for errors (F12)

**5.3 Production Build**
```bash
npm run build
```
✅ Should complete successfully
✅ Creates `build/` directory
✅ No errors or warnings

**5.4 Backend Integration**
```bash
# Terminal 1:
python run.py

# Terminal 2:
npm run dev
```
✅ Frontend connects to backend
✅ Can log in
✅ API calls work
✅ No CORS errors

**5.5 End-to-End Tests**
```bash
npm run test:e2e
```
✅ All tests pass
✅ No timeout errors

### Expected Test Results

All of the above should succeed. If any fail, see Troubleshooting section below.

---

## Step 6: Commit the Changes

Once all tests pass:

```bash
# Check what changed
git status
git diff vite.config.ts
git diff tsconfig.json

# Stage all changes
git add .

# Commit with clear message
git commit -m "refactor: Rename src/ to frontend/ for consistency

- Rename src/ directory to frontend/
- Update vite.config.ts paths
- Update tsconfig.json include patterns
- Update documentation references
- All tests passing

Improves monorepo clarity by matching backend/ naming convention."

# Verify commit
git log -1 --stat
```

---

## Step 7: Push and Verify

```bash
# Push to branch
git push origin your-branch-name

# Or push to main if confident
git push origin main
```

### Post-Push Verification

1. **Check GitHub UI:**
   - Verify frontend/ directory appears
   - Check file history preserved
   - Review the diff

2. **If using CI/CD:**
   - Wait for GitHub Actions to run
   - Verify all workflows pass
   - Check for any deployment issues

---

## Troubleshooting

### Issue: npm run dev fails with "Cannot find module"

**Cause:** Vite config still references old `src/` path

**Solution:**
```bash
# Check vite.config.ts
grep "src" vite.config.ts

# Update any remaining src/ references to frontend/
```

### Issue: TypeScript errors "Cannot find module '@/*'"

**Cause:** tsconfig.json path mapping not updated

**Solution:**
```json
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./frontend/*"]  // ← Ensure this uses frontend
    }
  }
}
```

### Issue: Build succeeds but page is blank

**Cause:** Base URL or public path misconfigured

**Solution:**
```typescript
// vite.config.ts
export default defineConfig({
  base: '/',  // Ensure this is correct
  // Check all path references
})
```

### Issue: Git shows entire directory as deleted/added

**This is normal!** Git renames appear as delete + add.

**To verify history preserved:**
```bash
# Check file history (use a specific file)
git log --follow frontend/components/App.tsx

# You'll see history from when it was in src/
```

### Issue: E2E tests fail with timeout

**Causes:**
1. Frontend didn't start properly
2. Port changed
3. Playwright config references src/

**Solution:**
```bash
# Check playwright.config.ts
grep "src" playwright.config.ts

# Verify frontend server starts:
npm run dev
# Should show: http://localhost:3000
```

### Issue: Import statements broken

**Cause:** Absolute imports using 'src' alias

**This shouldn't happen** if you:
- Updated tsconfig.json paths correctly
- Imports use relative paths or configured alias (@/)

**Solution:**
```bash
# Search for problematic imports
grep -r "from 'src/" frontend/

# Update to use alias or relative path
```

---

## Rollback Plan

If you encounter critical issues:

### Immediate Rollback

```bash
# Undo the rename
mv frontend src

# Revert config changes
git checkout vite.config.ts tsconfig.json package.json

# Test
npm run dev
```

### Full Rollback from Commit

```bash
# Revert the commit
git revert HEAD

# Or reset to before migration
git reset --hard HEAD~1

# Verify
npm run dev
python -m pytest
```

---

## Best Practices

### Do's

✅ **Commit beforehand** - Clean working tree
✅ **Test thoroughly** - All 5 testing steps
✅ **Update docs** - Keep documentation accurate
✅ **Clear commit message** - Explain what and why
✅ **Coordinate with team** - If working with others

### Don'ts

❌ **Don't rename during active development** - High risk of conflicts
❌ **Don't skip testing** - Could break production
❌ **Don't rename without updating configs** - Will break builds
❌ **Don't forget documentation** - Confuses contributors

---

## Post-Migration

### Update Development Habits

If you have scripts or aliases that reference `src/`:

```bash
# Example: Update your bash aliases
# Before: alias goto-frontend="cd ~/ProjectGoat/src"
# After:  alias goto-frontend="cd ~/ProjectGoat/frontend"
```

### Update Bookmarks/Notes

- IDE workspace settings
- Personal notes/documentation
- Development guides

### Team Communication

If working with others:
- Announce the change
- Update team documentation
- Help teammates with migration
- Point them to this guide

---

## Verification Checklist

Use this checklist to ensure complete migration:

- [ ] src/ directory renamed to frontend/
- [ ] vite.config.ts updated
- [ ] tsconfig.json updated
- [ ] package.json updated (if needed)
- [ ] .gitignore updated (if needed)
- [ ] .prettierignore updated (if needed)
- [ ] docs/guides/frontend-development.md updated
- [ ] .github/CONTRIBUTING.md updated
- [ ] TypeScript compilation passes (`npx tsc --noEmit`)
- [ ] Dev server starts (`npm run dev`)
- [ ] Frontend loads in browser
- [ ] Production build works (`npm run build`)
- [ ] E2E tests pass (`npm run test:e2e`)
- [ ] Backend integration works
- [ ] All changes committed
- [ ] Tests pass on CI/CD (if applicable)

---

## Timeline

**Estimated Time:**
- Preparation & backup: 10 minutes
- Rename & config updates: 30 minutes
- Testing: 60-90 minutes
- Documentation updates: 20 minutes
- Commit & push: 10 minutes
- **Total: 2-3 hours**

---

## When to Do This

**Good Times:**
- ✅ During slow development period
- ✅ At start of sprint
- ✅ When working on a feature branch
- ✅ After major release

**Bad Times:**
- ❌ During active feature development
- ❌ Right before a deadline
- ❌ When multiple people working on frontend
- ❌ During production issues

---

## References

- [FastAPI Full Stack Template](https://github.com/fastapi/full-stack-fastapi-template) - Uses frontend/ directory
- [Vite Configuration](https://vitejs.dev/config/) - Vite path configuration
- [TypeScript Path Mapping](https://www.typescriptlang.org/tsconfig#paths) - tsconfig.json paths

---

## Questions?

If you have questions during migration:
1. Check Troubleshooting section above
2. Review each step carefully
3. Test at each stage
4. Can always rollback if needed

---

**Status:** Ready to implement when needed
**Risk Level:** Medium (multiple config changes)
**Reversibility:** High (easy to rollback)
**Dependencies:** None (can do anytime)
