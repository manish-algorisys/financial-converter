# Environment Setup Guide

## Quick Setup for OPENAI_API_KEY

### Step 1: Install python-dotenv

```bash
pip install python-dotenv
# Or install all dependencies
pip install -r requirements.txt
```

### Step 2: Create .env file

Create a file named `.env` in the project root (same directory as `app.py`):

```bash
# Copy the template
cp .env.template .env
```

### Step 3: Add your OpenAI API Key

Edit the `.env` file and replace the placeholder:

```env
# OpenAI Configuration (Required for AI Excel Generation)
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

**Get your API key from:** https://platform.openai.com/api-keys

### Step 4: Verify Setup

Run this Python script to verify:

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if api_key:
    print(f"✅ API Key loaded: {api_key[:10]}...")
else:
    print("❌ API Key not found!")
```

Or use the test script:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ Key found!' if os.getenv('OPENAI_API_KEY') else '❌ Key not found!')"
```

### Step 5: Start the API

```bash
python app.py
```

You should see:

```
INFO - AI extractor initialized successfully
INFO - Starting Flask API on port 5000
```

If you see an error, the key wasn't loaded properly.

---

## Troubleshooting

### Issue: "OpenAI API key not provided"

**Cause:** .env file not found or not in the correct location

**Solution:**

1. Check `.env` is in the same directory as `app.py`
2. Verify the file is named exactly `.env` (not `.env.txt`)
3. Make sure `OPENAI_API_KEY` is spelled correctly
4. Restart the Flask API after creating/editing `.env`

### Issue: .env file not visible

**Windows:**

```bash
# Show hidden files in File Explorer
# Or create via command line:
echo OPENAI_API_KEY=sk-your-key-here > .env
```

**Linux/Mac:**

```bash
# .env files are hidden by default (start with .)
ls -la  # Shows hidden files
nano .env  # Edit with nano
```

### Issue: API key has special characters

If your API key contains special characters, **don't** use quotes in `.env`:

```env
# ✅ Correct
OPENAI_API_KEY=sk-proj-abc123_xyz789

# ❌ Wrong
OPENAI_API_KEY="sk-proj-abc123_xyz789"
```

### Issue: Working in different directory

If you're running from a different directory, specify the .env path:

```python
from dotenv import load_dotenv
from pathlib import Path

# Load .env from specific directory
env_path = Path('/path/to/project') / '.env'
load_dotenv(dotenv_path=env_path)
```

---

## Alternative: Set Environment Variable Directly

If you don't want to use .env file:

### Windows (PowerShell):

```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
python app.py
```

### Windows (Command Prompt):

```cmd
set OPENAI_API_KEY=sk-your-key-here
python app.py
```

### Linux/Mac:

```bash
export OPENAI_API_KEY="sk-your-key-here"
python app.py
```

**Note:** Environment variables set this way are temporary (lost when you close the terminal).

---

## Security Best Practices

1. **Never commit .env to Git:**

   ```bash
   # .gitignore should contain:
   .env
   ```

2. **Use .env.template for sharing:**

   ```bash
   # Share this file (without actual keys)
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Rotate keys periodically:**

   - Generate new keys at https://platform.openai.com/api-keys
   - Delete old keys

4. **Set usage limits:**
   - Configure spending limits in OpenAI dashboard
   - Monitor usage regularly

---

## Verification Checklist

- [ ] `python-dotenv` installed
- [ ] `.env` file created in project root
- [ ] `OPENAI_API_KEY` added to `.env`
- [ ] No quotes around the key value
- [ ] No spaces before/after `=`
- [ ] `.env` in `.gitignore`
- [ ] Flask API starts without errors
- [ ] Test script confirms key is loaded

---

## Quick Test

After setup, test the AI extraction:

```bash
# 1. Start API
python app.py

# 2. In another terminal, run test
python test_ai_excel.py

# Should see:
# ✅ AI extractor is initialized
```

---

**Need help?** Check [AI_EXCEL_QUICKSTART.md](AI_EXCEL_QUICKSTART.md) for full usage guide.
