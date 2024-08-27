import requests
from bs4 import BeautifulSoup as bs
import pickle
import re
import os
from matplotlib import pyplot as plt

rank_page_dirname = 'rank_pages'
player_page_dirname = 'player_pages'

solo_points_map = {}
team_points_map = {}

player_1_elo_map = {}
player_2_elo_map = {}
player_3_elo_map = {}
player_4_elo_map = {}

player_1_alltime_wins_map = {}
player_1_alltime_loss_map = {}
player_2_alltime_wins_map = {}
player_2_alltime_loss_map = {}
player_3_alltime_wins_map = {}
player_3_alltime_loss_map = {}
player_4_alltime_wins_map = {}
player_4_alltime_loss_map = {}
# ffa_elo_map = {}


if False:
  pagen = 1

  refs = []

  savefile = open('refs', 'wb')
  
  if not os.path.exists(rank_page_dirname):
    os.mkdir(rank_page_dirname)
                  
  while True:
    
    req_url = 'https://aoe4world.com/leaderboard/rm_solo?page={}'.format(pagen)
    page = requests.get(req_url)
    
    # Store pages
    pagefile = open('{}/{}'.format(rank_page_dirname, pagen), 'wb')
    pickle.dump(page, pagefile)
    pagefile.close()

    soup = bs(page.content, 'html.parser')
    
    table = soup.find('table', { 'class' : 'table-auto w-full whitespace-nowrap mt-4'})

    if not table is None:
      rows = table.findAll('tr')
      # print(len(rows))
      for row in rows[1:]:
        # print(row)
        cells = row.findAll('td')
        # print(len(cells))
        namecell = cells[1]
        
        link = namecell.find('a', {'class': 'underline-offset-2 hover:underline'})
        
        ref = link['href']
        refs.append(ref)
        
    else:
      break
    
    print('Scraped {} pages'.format(pagen))
    pagen += 1


  # Done with scraping
  print('{} players in {} pages'.format(len(refs), pagen))
  pickle.dump(refs, savefile)
  
elif False:
  
  savefile = open('refs', 'rb')
  refs = pickle.load(savefile)
  savefile.close()

  pattern = re.compile('/players/([0-9]*)-.*')
  
  if not os.path.exists(player_page_dirname):
    os.mkdir(player_page_dirname)
    
  for ref in refs:
    m = pattern.match(ref)
    assert(m is not None)
    id = m.group(1)
    # print(id)
    
    req_url = 'https://aoe4world.com{}'.format(ref)
    
    page = requests.get(req_url)
    
    # Store pages
    pagefile = open('{}/{}'.format(player_page_dirname, id), 'wb')
    pickle.dump(page, pagefile)
    pagefile.close()
    
    # print(req_url)
    # break

elif False:
    
  # Load refs to player IDs
  savefile = open('refs', 'rb')
  refs = pickle.load(savefile)
  savefile.close()

  pattern = re.compile('/players/([0-9]*)-.*')

  # Load data for each player from saved files
  for ref in refs:
    m = pattern.match(ref)
    assert(m is not None)
    id = int(m.group(1))

    # print(id)

    # Load pages for each player
    pagefile = open('{}/{}'.format(player_page_dirname, id), 'rb')
    page = pickle.load(pagefile)
    pagefile.close()

    soup = bs(page.content, 'html.parser')

    # Find solo ranking Points
    # First, find the bigger 'Solo Ranked' div
    # Second, find the part with points (for this season)
    # Third, go up one and then go down to the score
    solo_rank_div = soup.find('h4', {'class': 'flex-auto text-white font-bold'}, string = 'Solo Ranked').parent.parent
    solo_cur_season_points_subdivs = solo_rank_div.findAll('div', string = 'Points')
    assert(len(solo_cur_season_points_subdivs) == 1)
    solo_cur_season_points_div = solo_cur_season_points_subdivs[0].parent
    solo_cur_season_points = solo_cur_season_points_div.find('div', {'class': 'text-md'})
    points = int(solo_cur_season_points.string)

    solo_points_map[id] = points
    
    # Find team ranked Points
    # Team points might be missing
    team_rank_div_elem = soup.find('h4', {'class': 'flex-auto text-white font-bold'}, string = 'Team Ranked')
    if team_rank_div_elem is not None:
      team_rank_div = team_rank_div_elem.parent.parent
      team_cur_season_points_subdivs = team_rank_div.findAll('div', string = 'Points')
      
      # Might be missing points for this season
      if len(team_cur_season_points_subdivs) != 0:
        assert(len(team_cur_season_points_subdivs) == 1)
        team_cur_season_points_div = team_cur_season_points_subdivs[0].parent
        team_cur_season_points = team_cur_season_points_div.find('div', {'class': 'text-md'})
        points = int(team_cur_season_points.string)
      
        team_points_map[id] = points
      
    # Now, find the solo ELO by a similar method
    # Apparently, solo ELO might be missing
    elo_div_elem = soup.find('h4', {'class': 'flex-auto text-white font-bold'}, string = 'Ranked Matchmaking Elo')
    if elo_div_elem is not None:
      elo_div = elo_div_elem.parent.parent
      elo_table = elo_div.find('table', {'class': 'table-auto whitespace-nowrap mt-4'})
      
      # 1v1 elo
      solo_elo_row_elem = elo_table.find('div', string = '1v1')
      if solo_elo_row_elem is not None:
        solo_elo_row = solo_elo_row_elem.parent.parent.parent
        cols = solo_elo_row.find_all('td')
        elo = int(cols[1].string)
        wins_loss = cols[2].find_all('span')
        wins = int(wins_loss[1].string[:-1])     # Chopping of final W/L letter
        loss = int(wins_loss[2].string[:-1])     # Chopping of final W/L letter
        
        player_1_elo_map[id] = elo
        player_1_alltime_wins_map[id] = wins
        player_1_alltime_loss_map[id] = loss
        
      # 2v2 ELO
      p2_elo_row_elem = elo_table.find('div', string = '2v2')
      if p2_elo_row_elem is not None:
        p2_elo_row = p2_elo_row_elem.parent.parent.parent
        cols = p2_elo_row.find_all('td')
        elo = int(cols[1].string)
        wins_loss = cols[2].find_all('span')
        wins = int(wins_loss[1].string[:-1])     # Chopping of final W/L letter
        loss = int(wins_loss[2].string[:-1])     # Chopping of final W/L letter
        
        player_2_elo_map[id] = elo
        player_2_alltime_wins_map[id] = wins
        player_2_alltime_loss_map[id] = loss
        
      # 3v3 ELO
      p3_elo_row_elem = elo_table.find('div', string = '3v3')
      if p3_elo_row_elem is not None:
        p3_elo_row = p3_elo_row_elem.parent.parent.parent
        cols = p3_elo_row.find_all('td')
        elo = int(cols[1].string)
        wins_loss = cols[2].find_all('span')
        wins = int(wins_loss[1].string[:-1])     # Chopping of final W/L letter
        loss = int(wins_loss[2].string[:-1])     # Chopping of final W/L letter
        
        player_3_elo_map[id] = elo
        player_3_alltime_wins_map[id] = wins
        player_3_alltime_loss_map[id] = loss
        
      # 4v4 ELO
      p4_elo_row_elem = elo_table.find('div', string = '4v4')
      if p4_elo_row_elem is not None:
        p4_elo_row = p4_elo_row_elem.parent.parent.parent
        cols = p4_elo_row.find_all('td')
        elo = int(cols[1].string)
        wins_loss = cols[2].find_all('span')
        wins = int(wins_loss[1].string[:-1])     # Chopping of final W/L letter
        loss = int(wins_loss[2].string[:-1])     # Chopping of final W/L letter
        
        player_4_elo_map[id] = elo
        player_4_alltime_wins_map[id] = wins
        player_4_alltime_loss_map[id] = loss
        
      # FFA ELO
      # ffa_elo_row_elem = elo_table.find('div', string = 'FFA')
      # if ffa_elo_row_elem is not None:
      #   ffa_elo_row = ffa_elo_row_elem.parent.parent.parent
      #   elo = int(ffa_elo_row.find_all('td')[1].string)

      #   ffa_elo_map[id] = elo
        
    # print('{} has {} points, {} elo'.format(id, points, elo))

    # break
    
  # Dump player data maps to files
  outfile = open('map_id_to_solo_points', 'wb')
  pickle.dump(solo_points_map, outfile)
  outfile.close()
  outfile = open('map_id_to_team_points', 'wb')
  pickle.dump(team_points_map, outfile)
  outfile.close()
  outfile = open('map_id_to_1p_elo', 'wb')
  pickle.dump(player_1_elo_map, outfile)
  outfile.close()
  outfile = open('map_id_to_2p_elo', 'wb')
  pickle.dump(player_2_elo_map, outfile)
  outfile.close()
  outfile = open('map_id_to_3p_elo', 'wb')
  pickle.dump(player_3_elo_map, outfile)
  outfile.close()
  outfile = open('map_id_to_4p_elo', 'wb')
  pickle.dump(player_4_elo_map, outfile)
  outfile.close()
  outfile = open('map_id_to_1p_wins', 'wb')
  pickle.dump(player_1_alltime_wins_map, outfile)
  outfile.close()
  outfile = open('map_id_to_2p_wins', 'wb')
  pickle.dump(player_2_alltime_wins_map, outfile)
  outfile.close()
  outfile = open('map_id_to_3p_wins', 'wb')
  pickle.dump(player_3_alltime_wins_map, outfile)
  outfile.close()
  outfile = open('map_id_to_4p_wins', 'wb')
  pickle.dump(player_4_alltime_wins_map, outfile)
  outfile.close()
  outfile = open('map_id_to_1p_loss', 'wb')
  pickle.dump(player_1_alltime_loss_map, outfile)
  outfile.close()
  outfile = open('map_id_to_2p_loss', 'wb')
  pickle.dump(player_2_alltime_loss_map, outfile)
  outfile.close()
  outfile = open('map_id_to_3p_loss', 'wb')
  pickle.dump(player_3_alltime_loss_map, outfile)
  outfile.close()
  outfile = open('map_id_to_4p_loss', 'wb')
  pickle.dump(player_4_alltime_loss_map, outfile)
  outfile.close()

else:
  
  infile = open('map_id_to_solo_points', 'rb')
  solo_points_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_team_points', 'rb')
  team_points_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_1p_elo', 'rb')
  player_1_elo_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_2p_elo', 'rb')
  player_2_elo_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_3p_elo', 'rb')
  player_3_elo_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_4p_elo', 'rb')
  player_4_elo_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_1p_wins', 'rb')
  player_1_alltime_wins_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_2p_wins', 'rb')
  player_2_alltime_wins_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_3p_wins', 'rb')
  player_3_alltime_wins_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_4p_wins', 'rb')
  player_4_alltime_wins_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_1p_loss', 'rb')
  player_1_alltime_loss_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_2p_loss', 'rb')
  player_2_alltime_loss_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_3p_loss', 'rb')
  player_3_alltime_loss_map = pickle.load(infile)
  infile.close()
  infile = open('map_id_to_4p_loss', 'rb')
  player_4_alltime_loss_map = pickle.load(infile)
  infile.close()
  
  ## Plotting matchmaking ELO vs Points/Rating
  ids = player_1_elo_map.keys()
  points = [solo_points_map[id] for id in ids]
  elos = [player_1_elo_map[id] for id in ids]

  fig, ax = plt.subplots()
  ax.plot(points, elos, '+', label = 'Actual ELO and points', markersize = 0.1)
  ax.set_xlabel('Points')
  ax.set_ylabel('ELO')

  ax.grid(which = 'both', axis = 'both')
  
  # Plot a 1:1 line from min to max
  min_elo_points = min([min(points), min(elos)])
  max_elo_points = max([max(points), max(elos)])
  ax.plot(range(min_elo_points, max_elo_points, 5), range(min_elo_points, max_elo_points, 5), '.', markersize = 1, label = 'ELO = Points')
  ax.plot(range(min_elo_points, max_elo_points, 5), [x + 100 for x in range(min_elo_points, max_elo_points, 5)], '.', markersize = 1, label = 'ELO = Points + 100')
  ax.plot(range(min_elo_points, max_elo_points, 5), [x - 100 for x in range(min_elo_points, max_elo_points, 5)], '.', markersize = 1, label = 'ELO = Points - 100')

  ax.legend()
  ax.set_title('Comparison of player 1v1 ranked ELO vs Points')
  fig.savefig('elo_vs_points.pdf', bbox_inches='tight')
  # plt.savefig('', bbox)

  ## Plot team points vs solo points
  ids = list(set(solo_points_map.keys()).intersection(set(team_points_map)))
  solo_points = [solo_points_map[id] for id in ids]
  team_points = [team_points_map[id] for id in ids]
  
  fig, ax = plt.subplots()
  ax.plot(solo_points, team_points, '+', label = 'Player data', markersize = 0.1)
  ax.set_xlabel('Solo Points')
  ax.set_ylabel('Team Points')

  ax.grid(which = 'both', axis = 'both')
  
  # Plot a 1:1 line from min to max
  min_points = min([min(solo_points), min(team_points)])
  max_points = max([max(solo_points), max(team_points)])
  ax.plot(range(min_points, max_points, 5), range(min_points, max_points, 5), '.', markersize = 1, label = 'y = x')
  ax.plot(range(min_points, max_points, 5), [x + 100 for x in range(min_points, max_points, 5)], '.', markersize = 1, label = 'y = x + 100')
  ax.plot(range(min_points, max_points, 5), [x - 100 for x in range(min_points, max_points, 5)], '.', markersize = 1, label = 'y = x - 100')

  ax.legend()
  ax.set_title('Comparison of player team Points vs solo Points')
  fig.savefig('team_vs_solo.pdf', bbox_inches='tight')

  ## Plot number of games played vs solo ELO
  ids = player_1_elo_map.keys()
  elos = [player_1_elo_map[id] for id in ids]
  wins = [player_1_alltime_wins_map[id] for id in ids]
  loss = [player_1_alltime_loss_map[id] for id in ids]
  games = [w + l for (w, l) in zip(wins, loss)]
    
  fig, ax = plt.subplots()
  ax.plot(elos, games, '+', label = 'Player data', markersize = 0.1)
  ax.set_xlabel('1v1 ELO')
  ax.set_ylabel('Games played (alltime)')
  # ax.set_ylim(top = 2000)
  ax.set_yscale('log')

  ax.grid(which = 'both', axis = 'both')

  ax.legend()
  ax.set_title('Comparison of games played by player 1v1 ELO')
  fig.savefig('games_vs_elo.pdf', bbox_inches='tight')
  
  ## Plot number of win% vs solo ELO
  ids = player_1_elo_map.keys()
  elos = [player_1_elo_map[id] for id in ids]
  wins = [player_1_alltime_wins_map[id] for id in ids]
  loss = [player_1_alltime_loss_map[id] for id in ids]
  perc = [w/(w + l) for (w, l) in zip(wins, loss)]
    
  fig, ax = plt.subplots()
  ax.plot(elos, perc, '+', label = 'Player data', markersize = 0.1)
  ax.set_xlabel('1v1 ELO')
  ax.set_ylabel('Win percentage (alltime)')

  ax.grid(which = 'both', axis = 'both')

  ax.legend()
  ax.set_title('Comparison of win percentage by player 1v1 ELO')
  fig.savefig('win_perc_vs_elo.pdf', bbox_inches='tight')

  # Plot win% vs number of games
  ids = player_1_elo_map.keys()
  elos = [player_1_elo_map[id] for id in ids]
  wins = [player_1_alltime_wins_map[id] for id in ids]
  loss = [player_1_alltime_loss_map[id] for id in ids]
  perc = [w/(w + l) for (w, l) in zip(wins, loss)]
  games = [(w + l) for (w, l) in zip(wins, loss)]
  
  fig, ax = plt.subplots()
  ax.plot(games, perc, '+', label = 'Player data', markersize = 0.1)
  ax.set_xlabel('Games played (alltime)')
  ax.set_ylabel('Win percentage (alltime)')
  ax.set_xscale('log')

  ax.grid(which = 'both', axis = 'both')

  ax.legend()
  ax.set_title('Comparison of win percentage by number of games played')
  fig.savefig('win_perc_vs_games.pdf', bbox_inches='tight')