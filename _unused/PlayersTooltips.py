#!/usr/bin/python
#=!= coding:UTF-8 =!=
'''
Simonced Urban Terror Launcher
simonced@gmail.com
This is a tool to be used by UrbanTErrorLauncher.
'''

#tooltips lib
from TreeViewTooltips import TreeViewTooltips    #great tooltips lib

#================
# we generalise the great class TreeViewTooltips
#================
class PlayersToolTips(TreeViewTooltips):

    #Constructor
    def __init__(self):
        #Will be updated at server status request at the same time as the window
        self.players = {}
        
        TreeViewTooltips.__init__(self)
        self.label.set_use_markup(False)    #to prevent wrong parsing from players names

    # 2. overriding get_tooltip()
    def get_tooltip(self, view_, column_, path_):
        tooltip = ""
        
        try:
            
            address = view_.get_model()[path_[0]][1]
            loop = 0
            for player in self.players[address]:
                tooltip += player.split('"')[1] + "\n"
                loop += 1
                if loop>6:
                    tooltip += "..."
                    break
        except:
            tooltip += "SERVER UNREACHABLE\n"        
            
        return tooltip
