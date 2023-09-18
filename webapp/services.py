# All requests from external services/website/API here

from webapp.models import *
from dotenv import load_dotenv


## Example API request
# def scoresSearch(daysFrom="3"):
#     load_dotenv()
#     ODDS_API = os.environ["ODDS_API"]

#     params = {"daysFrom": daysFrom, "apiKey": ODDS_API}
#     baseUrl = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/scores"
#     response = requests.get(baseUrl, params=params)
#     json = response.json()
#     return json