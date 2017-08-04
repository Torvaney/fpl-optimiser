import numpy as np
import pandas as pd
import pulp
import os
import argparse
import warnings

from common import DATA_DIR


def add_position_dummy(df):
    for p in df.position.unique():
        df['is_' + str(p).lower()] = np.where(df.position == p, int(1), int(0))
    return df


def add_team_dummy(df):
    for t in df.team_id.unique():
        df['team_' + str(t).lower()] = np.where(df.team_id == t, int(1), int(0))
    return df


def get_optimal_squad(data, formation='2-5-5-3', budget=100.0, season='2016/17',
                      use_now_cost=False, optimise_on='total_points'):
    min_player_cost = 4.
    n_players = sum(int(i) for i in args.formation.split('-'))
    max_budget = 100 - (15 - n_players)*min_player_cost

    if budget is None:
        budget = max_budget

    if budget > max_budget:
        warnings.warn('Supplied budget exceeds expected maximum of '
                      '{0}'.format(max_budget))

    season_stats = (
        data
        .loc[lambda df: df.season_name == season]
        .reset_index()
        .assign(cost=lambda df: (df.now_cost / 10.) if use_now_cost else (df.start_cost / 10.))
        .pipe(add_position_dummy)
        .pipe(add_team_dummy)
    )

    players = season_stats.full_name

    # initalise the problem
    fpl_problem = pulp.LpProblem('FPL', pulp.LpMaximize)

    # create a dictionary of pulp variables with keys from names
    x = pulp.LpVariable.dict('x_ % s', players, lowBound=0, upBound=1,
                             cat=pulp.LpInteger)

    # player score data
    player_points = dict(
        zip(season_stats.full_name, np.array(season_stats[optimise_on])))

    # objective function
    fpl_problem += sum([player_points[i] * x[i] for i in players])

    # constraints
    position_names = ['gk', 'def', 'mid', 'fwd']
    position_constraints = [int(i) for i in formation.split('-')]

    constraints = dict(zip(position_names, position_constraints))
    constraints['total_cost'] = budget
    constraints['team'] = 3

    # could get straight from dataframe...
    player_cost = dict(zip(season_stats.full_name, season_stats.cost))
    player_position = dict(zip(season_stats.full_name, season_stats.position))
    player_gk = dict(zip(season_stats.full_name, season_stats.is_goalkeeper))
    player_def = dict(zip(season_stats.full_name, season_stats.is_defender))
    player_mid = dict(zip(season_stats.full_name, season_stats.is_midfielder))
    player_fwd = dict(zip(season_stats.full_name, season_stats.is_forward))

    # apply the constraints
    fpl_problem += sum([player_cost[i] * x[i] for i in players]) <= float(constraints['total_cost'])
    fpl_problem += sum([player_gk[i] * x[i] for i in players]) == constraints['gk']
    fpl_problem += sum([player_def[i] * x[i] for i in players]) == constraints['def']
    fpl_problem += sum([player_mid[i] * x[i] for i in players]) == constraints['mid']
    fpl_problem += sum([player_fwd[i] * x[i] for i in players]) == constraints['fwd']

    for t in season_stats.team_id:
        player_team = dict(
            zip(season_stats.full_name, season_stats['team_' + str(t)]))
        fpl_problem += sum([player_team[i] * x[i] for i in players]) <= constraints['team']

    # solve the thing
    fpl_problem.solve()

    total_points = 0.
    total_cost = 0.
    optimal_squad = []
    for p in players:
        if x[p].value() != 0:
            total_points += player_points[p]
            total_cost += player_cost[p]

            optimal_squad.append({
                'name': p,
                'position': player_position[p],
                'cost': player_cost[p],
                'points': player_points[p]
            })

    solution_info = {
        'formation': formation,
        'total_points': total_points,
        'total_cost': total_cost
    }

    return optimal_squad, solution_info

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--formation', default='2-5-5-3', type=str,
                        help='What formation should be used')
    parser.add_argument('--budget', default=None, type=float,
                        help='What is the maximum cost of the squad')
    parser.add_argument('--season', default='2016/17', type=str,
                        help='What season should be optimised.')
    parser.add_argument('--now-cost', action='store_true',
                        help='Use the current season\'s player cost.')
    parser.add_argument('--optimise-on', default='total_points', type=str,
                        help='What value should be optimised.')
    parser.add_argument('--exclude-players', default='', type=str,
                        help='Names of players to exclude, separated by `-`')
    args = parser.parse_args()

    exclude_players = args.exclude_players.split('-')
    player_info = pd.read_csv(os.path.join(DATA_DIR, 'fpl_history.csv'))
    player_info = player_info.loc[lambda df: ~df['full_name'].isin(exclude_players)]

    squad, soln = get_optimal_squad(player_info,
                                    formation=args.formation,
                                    budget=args.budget,
                                    season=args.season,
                                    use_now_cost=args.now_cost,
                                    optimise_on=args.optimise_on)

    # Prettify optimised squad
    positions = pd.read_csv(os.path.join(DATA_DIR, 'positions.csv'))
    squad = (
        pd.DataFrame(squad)
        .merge(positions, left_on='position', right_on='singular_name')
        .sort_values(by='id')  # sort by position id (GKs first)
        .reset_index(drop=True)
        [['position', 'name', 'cost', 'points']]  # reorder columns
    )
    squad.columns = [col.capitalize() for col in squad.columns]

    # Display output
    print(squad.to_string(index=False))
    print('')  # extra line break
    for key, val in soln.items():
        pretty_key = key.replace('_', ' ').capitalize()
        print('{0}:\t{1}'.format(pretty_key, val))
