# To be done / to be fixed #
## Easy and fast ##
  * ~~Actually, if we update a line, it duplicates the original line. Then you have to delete the original. I don't update lines often so I didn't bother to do a real edit function~~
  * ~~The | (pipe) character is forbidden for instance in the server name, has to be encoded in the txt file at save process~~
    * Actually replaced by the = sign. It's not needed at display anyway as it's the online server name that's being used.
  * ~~Adding colors depending of the game type~~
  * ~~Adding the IP of a server could query the server name so that it's not entered by the user~~
  * ~~Displaying the server name in colors like in UrbanTerror servers browser~~
  * Doing the same color display for players names in detailed view.

## A bit more complex ##
  * ~~Threading the refresh, so that each line appears one by one while the next servers are being queried~~
  * ~~Simply launching the game, and loging the servers played to add them automaticaly~~
    * Done, but have to be carefully tested + Detecting the server gametype and assigning it to the list, actually, AUTO is assigned.
  * Adding a Rcon feature
  * Adding a friend list