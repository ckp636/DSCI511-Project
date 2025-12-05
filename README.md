# DSCI511-Group5 Project
1. Navigate to the project folder <cd <folder>>
2. python -m http.server 8000
3. run http://localhost:8000.

[Project Structure]
- {index.html, script.js, style.css} are used for display data from json
- {loader-master.py} Python script used for web scraping. It collects data from external sources and saves it in JSON format for display.

[INFO] Fetching classification: Geography/State -> https://datausa.io/about/classifications/Geography/State
  Found 56 results
[INFO] Fetching classification: Geography/County -> https://datausa.io/about/classifications/Geography/County
  Found 3233 results
[INFO] Fetching classification: University/University -> https://datausa.io/about/classifications/University/University
  Found 7770 results

[Challenges]
- DataUS.io pages contain many React elements which can prevent scrapping using only BeautifulSoup. Selenium can be used to potentially overcome this.
- There are missing data from lesser known locations and universities.
- The dataset do not contain explicit linking information (eg. city belongs to which county and state, university is in which state ). The current temporary fix is to use an external dicationary containing state names and abbreviations for linking using slugs.
- Outdated data, mostly from 2022 and 2023.




