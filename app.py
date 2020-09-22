"""Python Web Development Techdegree Project 2 - Basketball Stats Tool
-----
By Steven Tagawa
September 2020
"""

# Imports
import os
import random

from constants import TEAMS, PLAYERS


def clean_data(lst):
    """Converts some values in a list of dictionaries of player data.

    Returns a new list, with any missing items filled with default values.  Any
    items in the list that are not dictionaries will be returned as-is.

    Arguments:
    lst -- the list of dictionaries on which to operate.

    Returns:
    a new list with the same structure as lst, with some of the values
    converted.
    """
    return_list = []
    for item in lst:
        # This shouldn't happen...
        if type(item) is not dict:
            return_list.append(item)
        else:
            return_list.append(convert(**item))
    return return_list


def convert(**kwargs):
    """Converts experience and height values from a dictionary of player data.

    Supplies default values for any missing or corrupted items.  Ignores any
    other key/value pairs.

    Keyword arguments:
    kwargs -- A dictionary of player data

    Default values:
    name -- "(unnamed player)"
    guardians -- "(None for [player])"
    experience -- False
    height -- 0

    Returns:
    A dictionary with the experience and height values converted to a bool and
    an int, respectively, and with the player's guardian(s) contained in a list.
    Any other key/value pairs are discarded.
    """
    entry = {}
    # Each try block will raise an exception if the value is not a string, or if
    # the dictionary entry is missing.  If an exception is raised, a warning
    # will be displayed and a default value will be substituted/added.

    # Since str() will not raise an exception (barring esoteric byte-decoding
    # cases), only need to check if the entry is missing, of if the entry is an
    # empty string or None.
    try:
        entry = {"name": str(kwargs["name"])}
        if entry["name"] == "" or entry["name"] == "None":
            entry["name"] = "(unnamed player)"
    except KeyError:
        show_warn("Name", "(unnamed player)")
        entry["name"] = "(unnamed player)"
    try:
        entry["guardians"] = kwargs["guardians"].split(" and ")
    except (KeyError, AttributeError):
        show_warn("Guardian", entry["name"])
        entry["guardians"] = f"(None for {entry['name']})"
    # If the experience item is already a boolean value, accept it as-is.
    if type(kwargs["experience"] != bool):
        # This try block will also display a warning if the string is not "YES"
        # or "NO".
        try:
            if kwargs["experience"].upper() == "YES":
                entry["experience"] = True
            elif kwargs["experience"].upper() == "NO":
                entry["experience"] = False
            else:
                show_warn("Experience", entry["name"])
                entry["experience"] = False
        except (KeyError, AttributeError):
            show_warn("Experience", entry["name"])
            entry["experience"] = False
    # This try block will only raise an error if the entry is missing.
    # Otherwise, the value is converted to a string before validation.
    try:
        entry["height"] = get_height(str(kwargs["height"]))
        if entry["height"] == 0:
            show_warn("Height", entry["name"])
    except KeyError:
        show_warn("Height", entry["name"])
        entry["height"] = 0
    return entry


def get_height(string):
    """Extracts the number representing a player's height.

    Substitutes a default value of 0 if the string does not start with a number.

    Arguments:
    string -- the string containing the player's height.

    Returns -- the player's height as an integer, if it exists, or 0.
    """
    height = ""
    for char in string:
        if ord(char) in range(48, 58):
            height += char
        else:
            break
    if height == "":
        return 0
    else:
        return int(height)


def show_warn(field, name):
    """Displays a warning if data is corrupted or missing."""
    print(
        f"Warning:  {field} data missing or corrupted for {name}.  Check your"
        f" data source.")
    return


def balance_teams(teams, players):
    """Distributes the players evenly among available teams.

    Arguments:
    teams -- A list of teams.
    players -- A list of players.  NOTE that the function destroys the list.

    Returns:
    A list containing an element for each team.  Each element is a list
    containing the team name and dictionaries for the players on that team.
    """
    team_list = [[team] for team in teams]
    players = calc_height_diff(players)
    # This is actually the minimum number of player per team.
    players_per_team = int(len(players)/len(teams))
    # If there aren't enough players to form the number of teams specified, tell
    # the user and exit.
    if players_per_team == 0:
        print(
            f"Sorry, {len(players)} players aren't enough to form {len(teams)} "
            f"teams.")
        return None
    exp_players_avail = calc_exp(players)
    inexp_players_avail = len(players) - exp_players_avail
    need_exp = True
    print(f"Working:  From {len(players)} players...")
    # Alternate between allocating experienced and inexperienced players, until
    # one pool or the other runs out.  Then just allocate the remaining players.
    for _ in range(players_per_team):
        # Cycle through the teams...
        for team in team_list:
            # If there are players of the type needed still available...
            if (
                (need_exp and exp_players_avail) or
                (not need_exp and inexp_players_avail)
            ):
                # ...cycle through the list of players, extract the first one
                # of the correct type and append it to the team list
                index = 0
                while index < len(players):
                    if players[index]["experience"] == need_exp:
                        team.append(players.pop(index))
                        if need_exp:
                            exp_players_avail -= 1
                        else:
                            inexp_players_avail -= 1
                        break
                    else:
                        index += 1
            # Otherwise, just grab the next player on the list.
            else:
                team.append(players.pop(0))
                # Once a pool runs out, no need to keep tracking it.  Players
                # will be drawn from the other pool automatically.
        # Flip the experience requirement.
        need_exp = not need_exp
    # After each team has been filled with the minimum number of players, if
    # there are players remaining, distribute them randomly.
    if len(players) > 0:
        order = random.sample(range(0, len(teams)), len(players))
        for team in order:
            team_list[team].append(players.pop(0))
    print(f"Created {len(team_list)} teams with at least {players_per_team}"
          f" players each.")
    return team_list


def calc_height_diff(players):
    """Calculates the differential between players' heights and the average.

    Arguments:
    players -- A list of players.

    Returns:
    The list of players with height differentials added, sorted by height
    differential.
    """
    # Find the average height of all the players first.
    avg_height, players = calc_avg_height(players)
    for player in players:
        # Add the differential to each player's dictionary.
        player["diff"] = abs(player["height"]-avg_height)
    # Sort the player dictionaries by height differential, so they can be
    # allocated in order.
    players = sort_dict(players, "diff")
    return players


def calc_avg_height(players):
    """Calculates the average height of all players with height data.

    Uses a list of player dictionaries; ignores any elements that are not
    dictionaries.

    Does not include players with no height data.  Changes the height data for
    players without height data to the average height of all other players.

    Arguments:
    players - A list of player dictionaries.

    Returns:
    The average height of all the players whose height > 0.  Also returns the
    list of player dictionaries, which may have been modified.
    """
    sum_height = 0
    players_counted = 0
    for player in players:
        # Only count players with heights.
        if (type(player) == dict) and (player["height"] > 0):
            sum_height += player["height"]
            players_counted += 1
    avg_height = sum_height / players_counted
    # Now substitute the average height for any players without height data.
    for player in players:
        if (type(player) == dict) and (player["height"] == 0):
            player["height"] = round(avg_height)
    return avg_height, players


def calc_exp(players):
    """Determines the number of players in a list are experienced.

    Uses a list of player dictionaries; ignores any elements that are not
    dictionaries.

    Arguments:
    players - A list of player dictionaries.

    Returns:
    The number of experienced players.
    """
    # Just run through all the player dictionaries looking for True in the
    # experience item.
    exp_players = 0
    for player in players:
        if (type(player) == dict) and (player["experience"]):
            exp_players += 1
    return exp_players


def sort_dict(dict_list, key):
    """Sorts a list of dictionaries according to the values in a specified key.

    Arguments:
    dict_list -- The list of dictionaries to sort.
    key -- The field on which to sort.

    The key field must be present in all dictionaries in the list.

    Returns:
    A sorted list of dictionaries, if successful; otherwise, the original list.
    """
    new_list = []
    try:
        # Find the dictionary with the highest value in the key field, insert it
        # at the beginning of the new list, repeat until done.
        while len(dict_list) > 0:
            high = 0
            for n, dic in enumerate(dict_list):
                if dic[key] > high:
                    high = n
            new_list.insert(0, dict_list.pop(high))
        return new_list
    except KeyError:
        return dict_list


def welcome():
    """Prints a welcome message."""
    print("=" * 40)
    print("Welcome to the Basketball Stats Tool")
    print("\nA Treehouse Python Techdegree Project")
    print("\nby Steven Tagawa")
    print("=" * 40)
    return


def goodbye():
    """Prints a goodbye message."""
    print("\n" + "=" * 40)
    print("Thanks for using the Basketball Stats Tool!")
    print("See you again soon!")
    print("=" * 40 + "\n")
    return


def clear():
    """Clears the screen (sometimes)."""
    os.system("cls" if "name" == "nt" else "clear")


def view_stats():
    """Asks the user if they want to view the statistics for a team.

    Returns:
    True if the user wants to view a team's statistics; False if they want to
    quit.
    """
    print("=" * 40)
    print("MAIN MENU\n")
    print("1.  See the statistics for a team")
    print("2.  Quit\n")
    response = check_response(input("What would you like to do?  "), ["1", "2"])
    if response == "1":
        return True
    return False


def check_response(string, response_list):
    """Checks the user's response, prompts until a valid response is given.

    Arguments:
    string -- the string to check
    response_list -- a list of valid responses.

    Returns:
    A valid string response.
    """
    while string not in response_list:
        string = input(
            "Sorry, that's not a valid response.  Please try again:  ")
    return string


def show_stats(team_list):
    """Shows the statistics for a selected team.

    Prompts the user to select a team, generates statistics for that team, and
    displays them.  Waits for the user to continue.

    Arguments:
    team_list -- the list of team data.
    """
    # First pick a team (adjusted for zero-based index).
    team = int(select_team(team_list)) - 1
    # Start with the header.
    print("\n" + "=" * 40)
    print(f"Statistics for the {team_list[team][0]}")
    print("-" * 40 + "\n")
    # Overall player statistics.
    print(f"Total players:  {len(team_list[team])-1}")
    exp = calc_exp(team_list[team])
    print(f"Total experienced players:  {exp}")
    exp = (len(team_list[team])-1) - exp
    print(f"Total inexperienced players:  {exp}")
    # Find and print the average player height.
    avg, _ = calc_avg_height(team_list[team])
    print(f"Average player height:  {round(avg, 1)} inches\n")
    # Print the player names.
    print(f"Players:  {get_names(team_list[team], 'name')}\n")
    # Print the guardian names.
    print(f"Guardians:  {get_names(team_list[team], 'guardians')}\n")
    # Wait for the user.
    input("Press [Enter] to continue.")
    return


def select_team(team_list):
    # Build the valid response list ["1", "2", "3", ...] based on the number of
    # teams.
    response_list = [str(n) for n in range(1, len(team_list)+1)]
    # Printing choices...
    print("\n" + "=" * 40)
    print("SELECT TEAM\n")
    for index, team in enumerate(team_list):
        print(f"{index+1}.  {team[0]}")
    # The check_response function will return a valid response, so just pass it
    # on.
    return check_response(
        input("\nWhich team would you like to view?  "), response_list)


def get_names(players, field):
    """
    Goes through a list of player dictionaries, extracts names and constructs a
    single string from them.  Ignores any elements of the list that are not
    dictionaries.

    Arguments:
    players -- The list of player dictionaries.
    field -- The field containing names.

    Returns:
    A string of names.
    """
    names = ""
    # Run through the dictionaries, appending names.
    for player in players:
        if type(player) == dict:
            # For a string, append the name.
            if type(player[field]) == str:
                names += player[field]
                # And, if it's a player, add if they are experienced or not.
                if field == "name":
                    if player["experience"]:
                        names += " (exp), "
                    else:
                        names += ", "
            else:
                # For a list, append each name in the list.
                for name in player[field]:
                    names += name + ", "
    # Strip the trailing comma and return.
    return names[:len(names)-2]


# EXECUTION STARTS HERE
if __name__ == "__main__":
    clear()
    welcome()
    player_list = clean_data(PLAYERS)
    team_list = balance_teams(TEAMS, player_list)
    while team_list:
        if view_stats():
            show_stats(team_list)
            clear()
            continue
        break
    goodbye()
# EXECUTION ENDS HERE
