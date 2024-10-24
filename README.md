# cs-back
backend for blog website

Some files are not stored on GitHub for safety reasons, and should be adjust according to the production environment:
- `env.sh`, which defines `DB_PATH`, the directory path where the database file is in (I use sqlite3 here so the file is .db); and `NOTE_REPO_PATH`, the path of the note repository.
- `SECRET`, which stores the secret for github webhook secret.