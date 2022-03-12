import os, sys
sys.path.insert(0, os.path.abspath(".."))

from datetime import date

from baseball_trips import (
	find_all_trips,
	Game,
	Trip,
)


def assert_equal(first, second):
	if first != second:
		raise Exception("{} does not equal {}".format(str(first), str(second)))


def test_find_all_trips_start_date():
	games = {
		"mariners": {
			date(2022, 4, 20): [Game("mariners", "dodgers", date(2022, 4, 20), "6:30")],
			date(2022, 4, 22): [Game("mariners", "dodgers", date(2022, 4, 22), "6:30")],
			date(2022, 4, 23): [Game("mariners", "dodgers", date(2022, 4, 23), "6:30")],
		},
		"giants": {
			date(2022, 4, 20): Game("giants", "dodgers", date(2022, 4, 20), "6:30"),
			date(2022, 4, 22): Game("giants", "dodgers", date(2022, 4, 22), "6:30"),
			date(2022, 4, 23): Game("giants", "dodgers", date(2022, 4, 23), "6:30"),
		},
	}
	# Full duration
	trips = find_all_trips(games, ["mariners"], date(2022, 4, 20), date(2022, 4, 23), 1, 3)
	expected = [
		Trip(["mariners"], date(2022, 4, 20), games["mariners"][date(2022, 4, 20)][0]),
		Trip(["mariners"], date(2022, 4, 22), games["mariners"][date(2022, 4, 22)][0]),
		Trip(["mariners"], date(2022, 4, 23), games["mariners"][date(2022, 4, 23)][0])
	]
	assert_equal(trips, expected)
	# Dead space before
	trips = find_all_trips(games, ["mariners"], date(2022, 4, 18), date(2022, 4, 23), 1, 3)
	expected = [
		Trip(["mariners"], date(2022, 4, 20), games["mariners"][date(2022, 4, 20)][0]),
		Trip(["mariners"], date(2022, 4, 22), games["mariners"][date(2022, 4, 22)][0]),
		Trip(["mariners"], date(2022, 4, 23), games["mariners"][date(2022, 4, 23)][0])
	]
	assert_equal(trips, expected)
	# Dead space after
	trips = find_all_trips(games, ["mariners"], date(2022, 4, 20), date(2022, 4, 25), 1, 3)
	expected = [
		Trip(["mariners"], date(2022, 4, 20), games["mariners"][date(2022, 4, 20)][0]),
		Trip(["mariners"], date(2022, 4, 22), games["mariners"][date(2022, 4, 22)][0]),
		Trip(["mariners"], date(2022, 4, 23), games["mariners"][date(2022, 4, 23)][0])
	]
	# Partial window
	trips = find_all_trips(games, ["mariners"], date(2022, 4, 22), date(2022, 4, 23), 1, 3)
	expected = [
		Trip(["mariners"], date(2022, 4, 22), games["mariners"][date(2022, 4, 22)][0]),
		Trip(["mariners"], date(2022, 4, 23), games["mariners"][date(2022, 4, 23)][0])
	]
	assert_equal(trips, expected)
	print("passed {}".format(str(test_find_all_trips_start_date)))


def test_find_all_trips_end_date():
	games = {
		"mariners": {
			date(2022, 4, 20): [Game("mariners", "dodgers", date(2022, 4, 20), "6:30")],
			date(2022, 4, 22): [Game("mariners", "dodgers", date(2022, 4, 22), "6:30")],
			date(2022, 4, 23): [Game("mariners", "dodgers", date(2022, 4, 23), "6:30")],
		},
		"giants": {
			date(2022, 4, 20): [Game("giants", "dodgers", date(2022, 4, 20), "6:30")],
			date(2022, 4, 22): [Game("giants", "dodgers", date(2022, 4, 22), "6:30")],
			date(2022, 4, 23): [Game("giants", "dodgers", date(2022, 4, 23), "6:30")],
		},
	}
	# Full set
	trips = find_all_trips(games, ["mariners", "giants"], date(2022, 4, 20), date(2022, 4, 23), 1, 1)
	expected = [
		Trip(["mariners", "giants"], date(2022, 4, 22), None, games=[games["mariners"][date(2022, 4, 22)][0], games["giants"][date(2022, 4, 23)][0]])
	]
	assert_equal(trips, expected)
	# No-op partial range, full set
	trips = find_all_trips(games, ["mariners", "giants"], date(2022, 4, 21), date(2022, 4, 23), 1, 1)
	expected = [
		Trip(["mariners", "giants"], date(2022, 4, 22), None, games=[games["mariners"][date(2022, 4, 22)][0], games["giants"][date(2022, 4, 23)][0]])
	]
	assert_equal(trips, expected)
	# Partial range, no results
	trips = find_all_trips(games, ["mariners", "giants"], date(2022, 4, 20), date(2022, 4, 22), 1, 1)
	expected = []
	assert_equal(trips, expected)
	print("passed {}".format(str(test_find_all_trips_end_date)))


def test_find_all_trips_max_break():
	games = {
		"mariners": {
			date(2022, 4, 20): [Game("mariners", "dodgers", date(2022, 4, 20), "6:30")],
			date(2022, 4, 22): [Game("mariners", "dodgers", date(2022, 4, 22), "6:30")],
			date(2022, 4, 23): [Game("mariners", "dodgers", date(2022, 4, 23), "6:30")],
		},
		"giants": {
			date(2022, 4, 20): [Game("giants", "dodgers", date(2022, 4, 20), "6:30")],
			date(2022, 4, 22): [Game("giants", "dodgers", date(2022, 4, 22), "6:30")],
			date(2022, 4, 23): [Game("giants", "dodgers", date(2022, 4, 23), "6:30")],
		},
	}
	# Partial set
	trips = find_all_trips(games, ["mariners", "giants"], date(2022, 4, 20), date(2022, 4, 23), 1, 1)
	expected = [
		Trip(["mariners", "giants"], date(2022, 4, 22), None, games=[games["mariners"][date(2022, 4, 22)][0], games["giants"][date(2022, 4, 23)][0]])
	]
	assert_equal(trips, expected)
	# Reversed partial set
	trips = find_all_trips(games, ["giants", "mariners"], date(2022, 4, 20), date(2022, 4, 23), 1, 1)
	expected = [
		Trip(["giants", "mariners"], date(2022, 4, 22), None, games=[games["giants"][date(2022, 4, 22)][0], games["mariners"][date(2022, 4, 23)][0]])
	]
	assert_equal(trips, expected)
	# Multiple Subsets
	trips = find_all_trips(games, ["mariners", "giants"], date(2022, 4, 20), date(2022, 4, 23), 1, 2)
	expected = [
		Trip(["mariners", "giants"], date(2022, 4, 20), None, games=[games["mariners"][date(2022, 4, 20)][0], games["giants"][date(2022, 4, 22)][0]]),
		Trip(["mariners", "giants"], date(2022, 4, 22), None, games=[games["mariners"][date(2022, 4, 22)][0], games["giants"][date(2022, 4, 23)][0]])
	]
	assert_equal(trips, expected)
	# All sets
	trips = find_all_trips(games, ["mariners", "giants"], date(2022, 4, 20), date(2022, 4, 23), 1, 3)
	expected = [
		Trip(["mariners", "giants"], date(2022, 4, 20), None, games=[games["mariners"][date(2022, 4, 20)][0], games["giants"][date(2022, 4, 22)][0]]),
		Trip(["mariners", "giants"], date(2022, 4, 22), None, games=[games["mariners"][date(2022, 4, 22)][0], games["giants"][date(2022, 4, 23)][0]]),
		Trip(["mariners", "giants"], date(2022, 4, 20), None, games=[games["mariners"][date(2022, 4, 20)][0], games["giants"][date(2022, 4, 23)][0]]),
	]
	assert_equal(trips, expected)
	print("passed {}".format(str(test_find_all_trips_max_break)))


def test_find_all_trips_min_break():
	games = {
		"mariners": {
			date(2022, 4, 20): [Game("mariners", "dodgers", date(2022, 4, 20), "6:30")],
			date(2022, 4, 22): [Game("mariners", "dodgers", date(2022, 4, 22), "6:30")],
			date(2022, 4, 23): [Game("mariners", "dodgers", date(2022, 4, 23), "6:30")],
		},
		"giants": {
			date(2022, 4, 20): [Game("giants", "dodgers", date(2022, 4, 20), "6:30")],
			date(2022, 4, 22): [Game("giants", "dodgers", date(2022, 4, 22), "6:30")],
			date(2022, 4, 23): [Game("giants", "dodgers", date(2022, 4, 23), "6:30")],
		},
	}
	# All sets
	trips = find_all_trips(games, ["mariners", "giants"], date(2022, 4, 20), date(2022, 4, 23), 1, 3)
	expected = [
		Trip(["mariners", "giants"], date(2022, 4, 20), None, games=[games["mariners"][date(2022, 4, 20)][0], games["giants"][date(2022, 4, 22)][0]]),
		Trip(["mariners", "giants"], date(2022, 4, 22), None, games=[games["mariners"][date(2022, 4, 22)][0], games["giants"][date(2022, 4, 23)][0]]),
		Trip(["mariners", "giants"], date(2022, 4, 20), None, games=[games["mariners"][date(2022, 4, 20)][0], games["giants"][date(2022, 4, 23)][0]]),
	]
	assert_equal(trips, expected)
	# Partial set
	trips = find_all_trips(games, ["mariners", "giants"], date(2022, 4, 20), date(2022, 4, 23), 2, 3)
	expected = [
		Trip(["mariners", "giants"], date(2022, 4, 20), None, games=[games["mariners"][date(2022, 4, 20)][0], games["giants"][date(2022, 4, 22)][0]]),
		Trip(["mariners", "giants"], date(2022, 4, 20), None, games=[games["mariners"][date(2022, 4, 20)][0], games["giants"][date(2022, 4, 23)][0]]),
	]
	assert_equal(trips, expected)
	# More restrictive partial set
	trips = find_all_trips(games, ["mariners", "giants"], date(2022, 4, 20), date(2022, 4, 23), 3, 3)
	expected = [
		Trip(["mariners", "giants"], date(2022, 4, 20), None, games=[games["mariners"][date(2022, 4, 20)][0], games["giants"][date(2022, 4, 23)][0]]),
	]
	assert_equal(trips, expected)
	# No results
	trips = find_all_trips(games, ["mariners", "giants"], date(2022, 4, 20), date(2022, 4, 23), 4, 4)
	expected = []
	assert_equal(trips, expected)
	print("passed {}".format(str(test_find_all_trips_min_break)))


def test_find_all_trips_double_header():
	games = {
		"mariners": {
			date(2022, 4, 20): [Game("mariners", "dodgers", date(2022, 4, 20), "6:30")],
			date(2022, 4, 22): [Game("mariners", "dodgers", date(2022, 4, 22), "6:30"), Game("mariners", "dodgers", date(2022, 4, 22), "10:30")],
		},
		"giants": {
			date(2022, 4, 20): [Game("giants", "dodgers", date(2022, 4, 20), "6:30")],
			date(2022, 4, 22): [Game("giants", "dodgers", date(2022, 4, 22), "6:30")],
			date(2022, 4, 23): [Game("giants", "dodgers", date(2022, 4, 23), "6:30")],
		},
	}
	# Minimum viable demonstration
	trips = find_all_trips(games, ["mariners", "giants"], date(2022, 4, 20), date(2022, 4, 23), 1, 1)
	expected = [
		Trip(["mariners", "giants"], date(2022, 4, 22), None, games=[games["mariners"][date(2022, 4, 22)][0], games["giants"][date(2022, 4, 23)][0]]),
		Trip(["mariners", "giants"], date(2022, 4, 22), None, games=[games["mariners"][date(2022, 4, 22)][1], games["giants"][date(2022, 4, 23)][0]])
	]
	assert_equal(trips, expected)
	print("passed {}".format(str(test_find_all_trips_double_header)))


def test_download_schedule_all():
	for team, team_id in TEAM_IDS.items():
		schedule = download_schedule(team, 2022)
		schedule = schedule.replace(" ", "").lower()
		if team in REPLACEMENTS:
			team = REPLACEMENTS[team]
		if schedule.count(team) < 81:
			assert_equal(team, schedule)
	print("passed {}".format(str(test_download_schedule_all)))


if __name__ == "__main__":
	test_find_all_trips_start_date()
	test_find_all_trips_end_date()
	test_find_all_trips_min_break()
	test_find_all_trips_max_break()
	test_find_all_trips_double_header()
	test_download_schedule_all()
