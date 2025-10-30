#%%
import os
import re
from pathlib import Path
from tkinter import Tk, filedialog
from docx import Document
from typing import Dict, List, Optional, Tuple

from SPR_v2 import *
from IPR_v2 import *

#%%

week_number = 42
    
print("\n" + "=" * 80 + "\n" + "INDIVIDUAL PROGRESS REPORTS" + "\n" + "=" * 80)

ipr = IndividualReports(week_number)
ipr.select_folder()
ipr.list_members()
ipr.compile_all()
ipr.compile_progress()   
ipr.compile_problems() 
ipr.compile_plans() 
    
#%%
ipr.get_individual_report(2)

#%%
print("\n" + "=" * 80 + "\n" + "SUB-TEAM PROGRESS REPORTS" + "\n" + "=" * 80)
spr = SubTeamReports(week_number)
spr.select_folder()
spr.list_teams()
spr.get_team_report()
spr.compile_all()
spr.compile_progress()
spr.compile_problems() 
spr.compile_plans() 

#%%
spr.get_team_report('COMPONENTS')
# spr.get_team_report('SYSTEM & SIMULATIONS')
# spr.get_team_report('MANUFACTURING METHODS')
# spr.get_team_report('AVIONICS & ELECTRONICS')
# spr.get_team_report('PR & ORGANIZATION')
# spr.get_team_report('TESTBED')
#%%