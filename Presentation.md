# Other pages #
  * [Requirements](Requirements.md)
  * [How to run](Setup.md)
  * [Known issues](Issues.md)

# Introduction #

I'm an Urban Terror player for about 1 year, and I developped a tool to help me connect easily to the server I play the most.
I did it in Python and GTK. It runs well under Linux (no XFire for the pinguin lol).
A Windows binary package is also available ;)
See in [downloads](http://code.google.com/p/urbanterrorlauncher/downloads/list) section.

# Actual features #

  * Insertion of servers in a list
  * Each server is queried to get status about map and players
  * Automatically adding new servers in the list after having played them (game have to be launched from the app)

### Screenshot of the current version : ###

  * Server list:

![http://a.imageshack.us/img17/173/urbanmterror077dev4.jpg](http://a.imageshack.us/img17/173/urbanmterror077dev4.jpg)


  * Buddies:

![http://a.imageshack.us/img267/5876/urbanmterror077dev5.jpg](http://a.imageshack.us/img267/5876/urbanmterror077dev5.jpg)


# Get it #

The current release can be found in the source tab here on this site.
For a full zipped package, please look for the last version in the [Downloads](http://code.google.com/p/urbanterrorlauncher/downloads/list) here.

# Release logs #

## 0.6 ##

  * Detailed player list view once a server is selected,
  * Server address as first field to prepare the name field auto-complete (for next release)

## 0.6.2 ##
  * Each server game type has it's own color, easier to find the game type you wanna play ;)
  * Auto complete of the server name from the IP:PORT activated

## 0.6.5 ##

  * Update works normaly now, a call to delete is simply done before
  * Server names are displayed with their colors like UrT Browser
  * Possibility to launch the game with no server selected, this way we can do anything we want.

## 0.7 ##

  * Adding automatically newly played servers into the list. Tests needed.

## 0.7.2 ##
  * Threading of servers list refresh for non blocking GUI.

## 0.7.6 ##
  * GUI update to be more eye candy. (add of icons)

## 0.7.7 ##
  * Buddy functions added.
    * Delete a buddy function still missong, but not a beag deal, to be done in next update.
  * Launching game threaded, so GUI not blocked anymore.
  * Preparation for in-game commands like `BUDDYADD toto` that will add the toto player in the buddies ;)

## 0.7.8 ##
  * Fixed:
    * Update server info that duplicated the server line,
    * Better sorting of number of players in server list.
  * Added:
    * Button to delete a buddy,
    * Possibility to delete servers or buddies with the DEL key,
    * Buddy status in the server list and in the players list

## 0.7.9 ##
  * Minor bugs corrections
  * Accurate ping for both Linux and Windows (should be the same for Mac)
  * Buddy icons update at adding or delete process for all areas (buddies, servers, players)

## 0.8 ##
  * New Feature! Search your buddies on any online server!
    * Needs more tests but works.