# FPL optimiser

Use linear programming to find the optimal fantasy football (soccer) squad.

This is not my idea and was originally (to my knowledge) by Martin Eastwood. You can find his blog post here: http://www.pena.lt/y/2014/07/24/mathematically-optimising-fantasy-football-teams/

The code was written on python 3.5.

## How to use it

This repo contains two main modules. `fetch_fpl_history` downloads the data from the fpl website. `optimise` allows you to find the optimal squad for a given season.

Usage is pretty simple. Just run the following two commands from the command line:
```
> python fetch_fpl_history.py
> python optimise.py
```

This will output an optimised squad, like the example below:
```
Position               Name  Cost  Points
Goalkeeper         Tom Heaton   5.0   149.0
Goalkeeper     Fraser Forster   5.0   134.0
  Defender    Charlie Daniels   5.0   134.0
  Defender  César Azpilicueta   6.5   170.0
  Defender        Gary Cahill   6.5   178.0
  Defender      Marcos Alonso   7.0   177.0
  Defender     Gareth McAuley   5.0   131.0
Midfielder          Joe Allen   5.5   118.0
Midfielder  Christian Eriksen   9.5   218.0
Midfielder      Bamidele Alli   9.5   225.0
Midfielder     Etienne Capoue   5.5   131.0
Midfielder   Robert Snodgrass   6.0   133.0
   Forward        Joshua King   7.5   178.0
   Forward      Jermain Defoe   8.0   166.0
   Forward    Roberto Firmino   8.5   180.0

Total cost:     100.0
Total points:   2422.0
Formation:      2-5-5-3
```

## Notes

Some notes on each of the modules

#### `fetch_fpl_history`

`fetch_fpl_history` fetches the data from the FPL website and saves it to `data/fpl_history.csv`.

This file includes a call to `time.sleep` so that we don't overload the FPL website's servers. Please bear this in mind and when scraping.

#### `optimise`

Once you have downloaded the data, you can run `python optimise.py` from the command line to find the optimal squad.

You can optionally change the optimiser's constraints with some command line arguments. For instance, if you wanted to run the optimiser with a different budget to the default £100, you can run `python optimise.py --budget 105`.

Another option is to supply a different formation to the default 2-5-5-3. For example if you wanted to optimise the first XI players (replacing the remaining squad places with £4.0 players), you could try `python optimise.py --formation 1-4-4-2` or `python optimise.py --formation 1-3-4-3`.

Or perhaps you've already decided which star striker (£10) you'll put in your team and want to optimise the rest of the squad `python optimise.py --formation 2-5-5-2 --budget 90`
