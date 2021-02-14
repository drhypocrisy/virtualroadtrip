import stravaio

def getaccesstoken():
    stravaio.strava_oauth2(client_id='61082', client_secret='ba97041b32cb047711da0321c9c85f3aef4db2f4')


if __name__ == '__main__':
    from stravaio import StravaIO

    # If the token is stored as an environment varible it is not neccessary
    # to pass it as an input parameters
    # client = StravaIO(access_token=STRAVA_ACCESS_TOKEN)
    client = StravaIO()

    # Get logged in athlete (e.g. the owner of the token)
    # Returns a stravaio.Athlete object that wraps the
    # [Strava DetailedAthlete](https://developers.strava.com/docs/reference/#api-models-DetailedAthlete)
    # with few added data-handling methods
    athlete = client.get_logged_in_athlete()

    # Dump athlete into a JSON friendly dict (e.g. all datetimes are converted into iso8601)
    athlete_dict = athlete.to_dict()

    # Store athlete infor as a JSON locally (~/.stravadata/athlete_<id>.json)
    athlete.store_locally()

    # Get locally stored athletes (returns a generator of dicts)
    local_athletes = client.local_athletes()