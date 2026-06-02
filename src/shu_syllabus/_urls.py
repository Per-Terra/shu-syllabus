import urllib.parse

BASE_URL = "https://aaaweb.shunan-u.ac.jp/aa_web/"
SEARCH_URL = urllib.parse.urljoin(BASE_URL, "syllabus/se0010.aspx?me=EU&opi=mt0010")
SYLLABUS_URL = urllib.parse.urljoin(BASE_URL, "syllabus/se0032.aspx")
ERROR_URL = urllib.parse.urljoin(BASE_URL, "customError.aspx")
