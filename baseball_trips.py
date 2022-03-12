import functools
import operator
import requests

from argparse import ArgumentParser
from collections import OrderedDict
from datetime import date, datetime, timedelta
from networkx import connected_components, Graph


TEAM_IDS = {
	"angels": 108,
	"astros": 117,
	"athletics": 133,
	"bluejays": 141,
	"braves": 144,
	"brewers": 158,
	"cardinals": 138,
	"cubs": 112,
	"diamondbacks": 109,  # dbacks on mlb.com
	"dodgers": 119,
	"giants": 137,
	"guardians": 114,
	"mariners": 136,
	"marlins": 146,
	"mets": 121,
	"nationals": 120,
	"orioles": 110,
	"padres": 135,
	"phillies": 143,
	"pirates": 134,
	"rangers": 140,
	"rays": 139,
	"reds": 113,
	"redsox": 111,
	"rockies": 115,
	"royals": 118,
	"tigers": 116,
	"twins": 142,
	"whitesox": 145,
	"yankees": 147,
}

REPLACEMENTS = {
	"diamondbacks": "d-backs",
}

class Game(object):
	def __init__(self, team, opponent, day, time):
		self.team = team
		self.day = day
		self.time = time
		self.opponent = opponent

	def game_day(self):
		# Used to help eliminate confusion from doubleheaders when combining trip options
		return "{}-{}".format(self.team, self.day)

	def __repr__(self):
		return "{} vs {}: {} {}".format(self.team, self.opponent, self.day, self.time)

	def __eq__(self, other):
		return str(self) == str(other)


class Trip(object):
	def __init__(self, teams, day, game=None, games=None):
		self.teams = teams
		self.start_date = day
		if games:
			self.games = games
		else:
			self.games = [game]

	def next_team(self):
		return self.teams[len(self.games)]

	def add_game(self, game, min_break):
		if abs(self.games[-1].day - game.day).days < min_break:
			return None
		return Trip(self.teams, self.start_date, games=(self.games + [game]))

	def invalid(self, day, max_break):
		return abs(self.games[-1].day - day).days >= max_break

	def complete(self):
		done = len(self.teams) == len(self.games)
		if done:
			self.end_date = self.games[-1].day
		return done

	def is_same_trip(self, game_day):
		for game in self.games:
			if game.game_day() == game_day:
				return True
		return False

	def __repr__(self):
		return "{}: {} - {}".format(self.start_date, self.teams, self.games)

	def __eq__(self, other):
		return str(self) == str(other)


class TripOptions(object):
	def __init__(self):
		self.trips = []
		self.games = set()

	def add_trip(self, trip):
		if not self.games or trip.games[0].day < self.start_date:
			self.start_date = trip.games[0].day
		if not self.games or trip.games[-1].day > self.end_date:
			self.end_date = trip.games[-1].day
		self.trips.append(trip)
		self.games.update([g.game_day() for g in trip.games])


def filter_teams(games, teams, day):
	out = {}
	for team in teams:
		out[team] = games[team].get(day, [])
	return out


def find_all_trips(games, teams, start_date, end_date, min_break, max_break):
	partial_trips = []
	valid_trips = []
	day = start_date
	while day <= end_date:
		days_games = filter_teams(games, teams, day)
		new_partials = []

		new_start = days_games[teams[0]]
		if new_start:
			for game in new_start:
				trip = Trip(teams, day, game)
				if trip.complete():
					valid_trips.append(trip)
				else:
					new_partials.append(trip)

		for trip in partial_trips:
			team_games = days_games[trip.next_team()]
			for game in team_games:
				new_trip = trip.add_game(game, min_break)
				if new_trip is not None:
					if new_trip.complete():
						valid_trips.append(new_trip)
					elif not new_trip.invalid(day, max_break):
						new_partials.append(new_trip)
			if not trip.invalid(day, max_break):
				new_partials.append(trip)

		partial_trips = new_partials
		day += timedelta(days=1)

	return valid_trips


def parse_games(teams, year):
	out = {}
	for team in teams:
		schedule = download_schedule(team, year)
		out[team] = parse_schedule(team, year, schedule)
	return out


def download_schedule(team, year):
	query_id = TEAM_IDS[team]
	query_params = {
		"team_id": query_id,
	    "home_team_id": query_id,
	    "display_in": "singlegame",
	    "ticket_category": "Tickets",
	    "site_section": "Default",
	    "sub_category": "Default",
	    "leave_empty_games": "true",
	    "event_type": "T",
	    "year": year,
	    "begin_date": "{}0201".format(year)
	}
	base_url = "https://www.ticketing-client.com/ticketing-client/csv/GameTicketPromotionPrice.tiksrv"
	query_pieces = []
	for k, v in query_params.items():
		query_pieces.append(str(k) + "=" + str(v))
	url = base_url + "?" + "&".join(query_pieces)
	resp = requests.get(url)
	if resp.status_code != 200:
		raise Exception(resp.text)
	return resp.text


def parse_schedule(team, year, schedule):
	lines = schedule.split("\n")[1:]
	split = [l.split(",") for l in lines if l]
	out = {}
	for s in split:
		game_time = s[1]
		matchup = s[3].split(" at ")[0].replace(" ", "").lower()
		day = datetime.strptime(s[0], "%m/%d/%y").date()
		game = Game(team, matchup, day, game_time)
		if not out.get(day):
			out[day] = []
		out[day].append(game)
	return out


def add_trip(trip, graph):
	for i, game in enumerate(trip.games):
		for other in trip.games[i+1:]:
			graph.add_edge(game.game_day(), other.game_day())


def graph_to_options(graph, trips):
	options = list(connected_components(graph))
	out = []
	for option in options:
		trip_option = TripOptions()
		for trip in trips:
			for game_day in option:
				if trip.is_same_trip(game_day):
					trip_option.add_trip(trip)
					break
		out.append(trip_option)
	return out

def combine_trips(trips, opponents, opponents_only):
	prioritized = Graph()
	normal = Graph()
	for trip in trips:
		if [g for g in trip.games if g.opponent in opponents]:
			add_trip(trip, prioritized)
		elif not opponents_only:
			add_trip(trip, normal)
	return (graph_to_options(prioritized, trips), graph_to_options(normal, trips))



def pretty_print(trip_options, include_trips, include_games):
	for option in trip_options:
		print("{} - {}".format(option.start_date, option.end_date))
		if include_trips or include_games:
			for trip in option.trips:
				print("\t{} - {}".format(trip.games[0].day, trip.games[-1].day))
				if include_games:
					for game in trip.games:
						print("\t\t{}".format(game))


# Requires `pip install networkx --user`
if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument("--min-break", type=int, default=1, help="minimum number of days between games, inclusive")
	parser.add_argument("--max-break", type=int, default=3, help="maximum number of days between games, inclusive")
	parser.add_argument("--start-date", default="2022-03-31", help="earliest trip date in `YYYY-MM-DD` format")
	# Note: all-star game is Tuesday, July 19, 2022
	parser.add_argument("--end-date", default="2022-12-01", help="latest trip date in `YYYY-MM-DD` format")
	parser.add_argument("--year", type=int, default=2022, help="year for baseball season, used for parsing files for different years' schedules")
	parser.add_argument("--team", action="append", default=[], help="ordered list of teams (no spaces), specified one at a time with this option", choices=TEAM_IDS.keys())
	parser.add_argument("--opponent", action="append", default=[], help="list of opponents (no spaces) to prioritize, specified one at a time with this option", choices=TEAM_IDS.keys())
	parser.add_argument("--opponents-only", action="store_true", help="only return trips that include games with specified opponents")
	parser.add_argument("--print-trips", action="store_true", help="print the date range options withing a group of trips")
	parser.add_argument("--print-games", action="store_true", help="print the specific games in each date range for a trip")
	parser.add_argument("--ordered", action="store_true", help="don't permit trips in the opposite order of games")
	args = parser.parse_args()

	games = parse_games(args.team, args.year)
	args.start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
	args.end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
	args.opponent = [REPLACEMENTS.get(t, t) for t in args.opponent]
	for_trips = find_all_trips(games, args.team, args.start_date, args.end_date, args.min_break, args.max_break)
	if args.ordered:
		all_trips = for_trips
	else:
		rev_trips = find_all_trips(games, list(reversed(args.team)), args.start_date, args.end_date, args.min_break, args.max_break)
		all_trips = for_trips + rev_trips
	prioritized, normal = combine_trips(all_trips, args.opponent, args.opponents_only)
	if args.opponent:
		prioritized.sort(key=lambda x: x.start_date)
		pretty_print(prioritized, args.print_trips, args.print_games)
		print("Found {} trips with opponents in {} groups".format(reduce(operator.add, [len(o.trips) for o in prioritized], 0), len(prioritized)))
	if not args.opponents_only:
		normal.sort(key=lambda x: x.start_date)
		pretty_print(normal, args.print_trips, args.print_games)
		print("Found {} trips in {} groups".format(reduce(operator.add, [len(o.trips) for o in normal], 0), len(normal)))
