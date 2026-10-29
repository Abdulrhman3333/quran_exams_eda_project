# Quran Exams in Jeddah: Results Explorer

This Streamlit app explores a sanitized, deterministic-pseudonym version of the Quran memorization exam dataset in Jeddah. It provides shared filters and eight pages covering overview trends, branches, sectors, mosques, teachers, privacy-safe student aggregates, COVID impact, seasonality, and methods.

## Install and run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
streamlit run app.py
```

Keep the original `exams_clean.csv` private. Generate the public dataset with:

```powershell
py sanitize_public_data.py
```

This writes `exams_clean_public.csv`, replacing all student, teacher, mosque, supervisor, halaqa, sector, and manager values with stable labels such as `Teacher 0001` and `Mosque 0007`. The app reads only `exams_clean_public.csv` with `encoding="utf-8-sig"`, removes duplicate exam IDs and invalid branches/malformed dates, and reports cleaning counts on the Data and Methods page.

The source `exams_clean.csv` must never be published. The public file contains pseudonyms rather than reversible encrypted values; repeated entities remain consistent for analysis, but the original names cannot be recovered from the public file without the private source.
