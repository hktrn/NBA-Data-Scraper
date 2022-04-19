
import pandas as pd
from bs4 import BeautifulSoup
from urllib import request


def gather_leaders(link):
    website = request.urlopen(link).read()
    soup = BeautifulSoup(website, 'lxml')

    entries = soup.find(
        'div', attrs={'class': 'data_grid', 'id': 'div_leaders'})
    categories = []
    names = []
    for entry in entries:
        # every other entry is '\n'
        if entry == '\n':
            pass
        # add the category and name to the lists
        else:
            category = entry.caption.text
            name = entry.a.text
            categories.append(category)
            names.append(name)
    # putting the data in categories and names into a dataframe
    winners = pd.DataFrame({'Player': names, 'Categories': categories})

    return winners


def gather(link):
    website = request.urlopen(link).read()
    soup = BeautifulSoup(website, 'lxml')

    # finding the statistics
    table = soup.find(
        'table', attrs={'class': 'sortable', 'id': 'per_game_stats'})

    table_headers = [header.text for header in table.find(
        'thead').find_all('th')]
    table_rows = table.find_all('tr')

    # collecting every row and column
    final_data = []
    for tr in table_rows:
        td = tr.find_all('td')
        row = [tr.text for tr in td]
        final_data.append(row)

    # exporting statitics
    data = pd.DataFrame(final_data, columns=table_headers[1:])
    data.to_excel('output.xlsx')
    return data

# Needed the leader category names to put in the column for dataframe


def leader_columns(link):
    website = request.urlopen(link).read()
    soup = BeautifulSoup(website, 'lxml')

    entries = soup.find(
        'div', attrs={'class': 'data_grid', 'id': 'div_leaders'})
    categories = []
    for entry in entries:
        # every other entry is '\n'
        if entry == '\n':
            pass
        else:
            category = entry.caption.text
            categories.append(category)

    return categories


def clean(data, link):

    # reading in the statistics
    data = pd.read_excel('output.xlsx')

    # removing unnamed column
    data.drop(columns=['Unnamed: 0'], axis=1, inplace=True)

    # Sorting players by their alphabetical order
    data.sort_values(by=['Player'], inplace=True)

    # Removing the total input of each player
    # Only keep what each player's statistics on respective team
    data.drop(data[data.Tm == 'TOT'].index, inplace=True)

    # Dropping missing players
    data.dropna(subset=['Player'], inplace=True)

    # Adding in the leader columns and assigning 'No' to everyone
    # collecting the leader columns
    columns = leader_columns(link)
    for column in columns:
        data[f"{column}_Leader"] = 'No'

    return data


def combine(data, leaders):
    name = []
    category = []
    # finding all leader winners
    for count in range(0, len(leaders)):
        name = leaders.iloc[count]['Player']
        category = leaders.iloc[count]['Categories']
        # if names matches, go to the leader column and replace 'No' to 'Yes'
        for idx, row in data.iterrows():
            if data.at[idx, 'Player'] == name:
                data.at[idx, f"{category}_Leader"] = 'Yes'
    return data


def convert(data):

    data = data.rename({'Pos': 'Position',
                        'Tm': 'Team',
                        'G': 'Games Played',
                        'GS': 'Games Started',
                        'MP': 'Minutes Played',
                        'FG': 'Field Goals',
                        'FGA': 'Field Goal Attemped',
                        'FG%': 'Field Goal Percentage',
                        '3P': '3-Point Field Goals',
                        '3PA': '3-Point Field Goal Attemps',
                        '3P%': '3-Point Field Goal Percentage',
                        '2P': '2-Point Field Goals',
                        '2PA': '2-Point Field Goal Attemps',
                        '2P%': '2-Point Field Goal Percentage',
                        'eFG%': 'Effective Field Goal Percentage',
                        'FT': 'Free Throws',
                        'FTA': "Free Throws Attemps",
                        'FT%': 'Free Throw Percentage',
                        'ORB': 'Offensive Rebounds',
                        'DRB': 'Defensive Rebounds',
                        'TRB': 'Total Rebounds',
                        'AST': 'Assists',
                        'STL': 'Steals',
                        'BLK': 'Blocks',
                        'TOV': 'Turnovers',
                        'PF': 'Personal Fouls',
                        'PTS': 'Points'}, axis=1)
    return data


def collect(link1, link2):
    data = gather(link1)
    cleaned = clean(data, link2)
    converted = convert(cleaned)
    leaders = gather_leaders(link2)
    combined = combine(converted, leaders)
    return combined


def get_data_1year(year):
    link = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
    leader = f"https://www.basketball-reference.com/leagues/NBA_{year}_leaders.html"
    result = collect(link, leader)
    result['Year'] = f'{year}'
    # Excel
    result.to_excel('1_ydata.xlsx', index=False)
    # CSV
    result.to_csv('1_ydata.csv', index=False)


def get_data(start, end):
    data = []
    # while loop to collect over the years
    while start <= end:
        link = f"https://www.basketball-reference.com/leagues/NBA_{start}_per_game.html"
        leader = f"https://www.basketball-reference.com/leagues/NBA_{start}_leaders.html"
        df = collect(link, leader)
        df['Year'] = f'{start}'
        data.append(df)
        start += 1
    result = pd.concat(data)
    # Excel
    result.to_excel('m_ydata.xlsx', index=False)
    # CSV
    result.to_csv('m_ydata.csv', index=False)


if __name__ == '__main__':
    get_data(2021, 2022)
    get_data_1year(2022)
