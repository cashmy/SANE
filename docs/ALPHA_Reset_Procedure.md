# ALPHA Reset Procedure

This procedure resets the local Stage 1 ALPHA state without adding any in-app reset control.

Use it when:

- the local SQLite data needs to be cleared
- schema changes make older ALPHA data invalid
- demo flows need a clean review queue
- frontend-local theme state should be reset for a clean demo

## Reset Steps

1. Stop any running frontend and backend dev servers.

2. Remove the local ALPHA SQLite database.

```powershell
Remove-Item "backend\sane_alpha.db" -ErrorAction SilentlyContinue
```

3. Clear the saved frontend theme preference if you want the UI to return to light mode.

In the browser devtools console for the frontend app:

```javascript
localStorage.removeItem("sane-theme");
```

4. Restart the backend so the schema and demo source data are recreated.

```powershell
Set-Location "backend"
& "d:/@Coding_Projects/Mult-Tech/SANE/.venv/Scripts/python.exe" -m uvicorn app.main:app --reload
```

5. Restart the frontend if needed.

```powershell
Set-Location "frontend"
npm run dev
```

## Validation After Reset

Run the project validation commands after a reset if you need to verify the local state and schema.

```powershell
Set-Location "backend"
& "d:/@Coding_Projects/Mult-Tech/SANE/.venv/Scripts/python.exe" -m pytest

Set-Location "../frontend"
npm run test:run
npm run build
```

## Notes

- This reset affects local ALPHA data only.
- No Gmail state, OAuth state, billing state, or external email actions are involved.
- The internal `Candidate` SQLAlchemy name is still used for this repair pass to reduce churn, but the ALPHA API and UI now treat these rows as source review units.