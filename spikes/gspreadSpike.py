import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']

credentials = ServiceAccountCredentials.from_json_keyfile_name('trap_auth.json', scope)

gc = gspread.authorize(credentials)

sh = gc.open("1unfh55eB4Y7yM0o90fDhiZviAmc1eeHk29b7YegmEY8")    # Can't open?