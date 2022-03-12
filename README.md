# baseball-trips
This repository contains a small script for finding baseball trips for combinations of home teams. It has options to dictate the dates, duration of the trip, and opponents played.

## Installation
Download the git repository and run `pip install -r requirements.txt --user` to install the dependencies.

## Usage
To see a full list of available options, run:
```
python baseball_trips.py -h
```
An example usage would be to run:
```
python baseball_trips.py --team reds --team guardians --team tigers
```
to find all date ranges where a trip following those teams in any order existed, then run:
```
python baseball_trips.py --team reds --team guardians --team tigers --start-date 2022-03-31 --end-date 2022-04-05 --print-trips --print-games
```
to see the specific games that are available in that date range.

## Output Format
The output format will be a list of date ranges, containing the minimum date and maximum date for each contiguous set of games. For example, if a trip could consist of a game on June 12th and June 14th or June 13th and June 15th, the date range would be June 12th to June 15th. Specifying `--print-trips` will further list both of the two options for the June 12th - June 15th date range that was found. Specifying `--print-games` will then output each of the games that comprise the trip. Sample output:
```
2022-03-31 - 2022-04-05
	2022-03-31 - 2022-04-02
		reds vs whitesox: 2022-03-31
		guardians vs d-backs: 2022-04-01
		tigers vs orioles: 2022-04-02
	2022-04-02 - 2022-04-04
		reds vs padres: 2022-04-02
		guardians vs cubs: 2022-04-03
		tigers vs bluejays: 2022-04-04
	2022-03-31 - 2022-04-04
		reds vs whitesox: 2022-03-31
		guardians vs d-backs: 2022-04-01
		tigers vs bluejays: 2022-04-04
	2022-03-31 - 2022-04-04
		reds vs whitesox: 2022-03-31
		guardians vs cubs: 2022-04-03
		tigers vs bluejays: 2022-04-04
	2022-04-02 - 2022-04-04
		tigers vs orioles: 2022-04-02
		guardians vs cubs: 2022-04-03
		reds vs royals: 2022-04-04
	2022-04-01 - 2022-04-04
		tigers vs yankees: 2022-04-01
		guardians vs cubs: 2022-04-03
		reds vs royals: 2022-04-04
	2022-04-02 - 2022-04-05
		tigers vs orioles: 2022-04-02
		guardians vs cubs: 2022-04-03
		reds vs mariners: 2022-04-05
	2022-04-01 - 2022-04-05
		tigers vs yankees: 2022-04-01
		guardians vs cubs: 2022-04-03
		reds vs mariners: 2022-04-05
```