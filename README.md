# Yahoo Fantasy API example workspace

This small scaffold shows how to authenticate and query Yahoo Fantasy (NBA) using the `yahoo-fantasy-api` and `yahoo-oauth` packages.

Setup
1. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `oauth2.example.json` to `oauth2.json` and fill in your `consumer_secret`.

```bash
cp oauth2.example.json oauth2.json
# edit oauth2.json and replace YOUR_CLIENT_SECRET_HERE with your secret
```

4. Run the OAuth helper (first run will open a browser to authorize):

```bash
python -m src.auth
```

5. Run the quick test to list NBA leagues for 2025:

```bash
python -m src.quick_test
```

Tests

Run pytest:

```bash
pytest -q
```

Notes
- Do NOT commit `oauth2.json` (it's in `.gitignore`).
- If you run into import errors within your editor, ensure your virtualenv is selected for the workspace interpreter.
