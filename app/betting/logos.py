#from _typeshed import NoneType
import boto3
import json
from thefuzz import fuzz
from thefuzz import process
import os
import ast

# Needs Aws Credentials to run this code
# Main fucntion is BestPossibleLogo() which takes help from GetLogoDataFromAws()


# The folder name in the AWS is the sport_key
# The file name which are in the folder are the teams name

aws_access_key = "AKIAW4VCOYGLZJ6JTVUO"
aws_secret_access = "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"
prefix_url = "https://sports-team-logos.s3.us-east-2.amazonaws.com/americanfootball_nfl/49ers.png"

league_code_dict = {
    'nfl': 'americanfootball_nfl',
    'ncaabaseball': 'ncaa',
    'ncaaf': 'ncaa',
    'mlb': 'baseball_mlb',
    'nhl': 'icehockey_nhl',
    'soccer': 'soccer',  # create aws bucket
    'wnba': 'wnba'  # create aws bucket
}

supported_leagues = [
    'ncaabaseball',
    'ncaaf',
    'golf',
    'mlb',
    'mma',
    'nfl',
    'nhl',
    'soccer',
    'tennis',
    'wnba'
]

aws_folder_names = [
    'americanfootball_nfl',
    'basketball_nba',
    'ncaa',
    'baseball_mlb',
    'icehockey_nhl',
    'Premier_League',
    'Bundesliga',
    'La Liga',
    'Ligue 1',
    'Serie A',
    'MLS'
]

# This function is the helper function for the Main Function and the Main fucntion is BestPossibleLogo()


def GetLogoDataFromAws(bucket_name):
    '''
    Input: Bucket Name from AWS
    Output: JSON Dictionary where keys will be the sport_key and values will be the list of names of team

    '''
    dc = {}
    session = boto3.Session(aws_access_key, aws_secret_access)
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for objects in bucket.objects.all():
        sportAndTeam = objects.key
        teamWithImageExtension = sportAndTeam.split("/")[1]
        sport = sportAndTeam.split("/")[0]
        team = teamWithImageExtension.split(".png")[0]
        if sport not in dc:
            dc[sport] = [team]
        else:
            dc[sport].append(team)

    return json.dumps(dc)


aws_team_names = GetLogoDataFromAws('sports-team-logos')


def match_team_ids(aws_team_names):

    aws_team_names = ast.literal_eval(aws_team_names)
    logo_dict = []

    json_data = open(os.path.join(
        'json_scripts', 'team_codes.json'), 'r')
    team_codes = json.load(json_data).get('data')

    supported_league_json = open(os.path.join(
        'json_scripts', 'supported_league_codes.json'), 'r')
    supported_league_json = json.load(supported_league_json).get('data')

    for x in range(len(team_codes)):
        team = team_codes[x]
        sport_acronym = team.get('sport_acronym')
        league_code = team.get('league_code')
        team_id = team.get('team_ID')
        team_name = team.get('team_name')
        if team_name == None:
            team_name = team.get('city')
        try:
            adjusted_team_name = team_name.strip().lower().replace(" ", "")
        except AttributeError:
            adjusted_team_name = ""

        league_match = False
        break_this_loop = False
        for league in supported_league_json:
            try:
                for x in league[sport_acronym]:
                    if x['code'] == league_code:
                        league_match = True
                        break_this_loop = True
                        break
            except:
                pass

            if break_this_loop:
                break

        if league_match:
            breakloop = False
            for folder in aws_folder_names:
                league = aws_team_names.get(folder)

                # gets down tot he team name level in aws folder
                for aws_team in league:
                    adjusted_aws_team = aws_team.strip().lower().replace(" ", "")
                    if adjusted_aws_team == adjusted_team_name:
                        dir = f'https://sports-team-logos.s3.us-east-2.amazonaws.com/{folder}/{aws_team}.png'
                        logo_dict.append({team_id: dir})
                        breakloop = True
                        break
                    if breakloop:
                        break
                if breakloop:
                    break

            # if loop did not break then we need to add the team later
            if not breakloop:
                logo_dict.append({team_id: None})

    return ({"data": logo_dict})


logo_dict = match_team_ids(aws_team_names)
print(logo_dict)


def BestPossibleLogo(oddsAPIJsonFile, bucketName):
    """
    Input:
    Takes a json file that will be OddAPI Data. Assuming after we load this json file we get a dictionary
    The 2nd parameter is the bucket name where we store the logos
    Output: Dictionary which will have only 1 key(sport_key) and the value of this will be a list of strings. 
    The length of this list will be 2 and this will be names of the teams with .png
    """
    oddApiDict = json.loads(oddsAPIJsonFile)
    LogoData = json.loads(GetLogoDataFromAws(bucketName))
    sport_key = oddApiDict["sport_key"]
    teamOne = oddApiDict["teams"][0]
    teamTwo = oddApiDict["teams"][1]
    AllOurSports = LogoData.keys()
    sport = process.extractOne(sport_key, AllOurSports)[0]
    AllOurTeam = LogoData[sport]
    A = process.extractOne(teamOne, AllOurTeam)
    B = process.extractOne(teamTwo, AllOurTeam)
    BestLogoTeamOne = ""
    BestLogoTeamTwo = ""
    if int(A[1]) < 50:
        BestLogoTeamOne = "None"
    else:
        BestLogoTeamOne = A[0]

    if int(B[1]) < 50:
        BestLogoTeamTwo = "None"
    else:
        BestLogoTeamTwo = B[0]
    return {sport: [BestLogoTeamOne + ".png", BestLogoTeamTwo + ".png"]}
