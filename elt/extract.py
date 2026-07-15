import requests
from config import API_KEY, COMPETITION_CODE
from loguru import logger

BASE_URL = "https://api.football-data.org/v4"


def extract_matches(competition_code: str) -> dict:
    """Fetch all matches for a given competition from football-data.org"""

    url = f"{BASE_URL}/competitions/{competition_code}/matches"
    headers = {"X-Auth-Token": API_KEY}

    logger.info(f"Extracting matches for competition: {competition_code}")

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    data = response.json()
    logger.info(f"Extracted {len(data['matches'])} matches.")

    return data


def extract_standings(competition_code: str) -> dict:
    """Fetch current standings for a given competition"""

    url = f"{BASE_URL}/competitions/{competition_code}/standings"
    headers = {"X-Auth-Token": API_KEY}

    logger.info(f"Extracting standings for competition: {competition_code}")

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    data = response.json()
    logger.info("Extracted standings successfully")
    return data


def extract_scorers(competition_code: str) -> dict:
    """Fetch top scorers for a given competition"""

    url = f"{BASE_URL}/competitions/{competition_code}/scorers"
    headers = {"X-Auth-Token": API_KEY}

    logger.info(f"Extracting top scorers for competition: {competition_code}")

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    data = response.json()
    logger.info(f"Extracted {len(data['scorers'])} scorers")

    return data


if __name__ == "__main__":
    # Quick smoke test of the three endpoints.
    matches = extract_matches(COMPETITION_CODE)
    standings = extract_standings(COMPETITION_CODE)
    scorers = extract_scorers(COMPETITION_CODE)
    logger.info(
        f"OK — {len(matches['matches'])} matches, "
        f"{len(standings['standings'][0]['table'])} standings rows, "
        f"{len(scorers['scorers'])} scorers"
    )
