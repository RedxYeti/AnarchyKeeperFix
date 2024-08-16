import unrealsdk
import os
from Mods.ModMenu import EnabledSaveType, Mods, ModTypes, RegisterMod, SDKMod, Options, Hook, Game
from typing import cast

from unrealsdk import FindObject, Log, UObject, GetEngine

class anarchystacks(SDKMod):
    Name: str = "KeepAnarchy"
    Author: str = "Sampletext282"
    Description: str = (
        "Lets you keep a set percentage of your Anarchy on Savequit."
    )
    Version: str = "0.0.9"
    Types: ModTypes = ModTypes.Utility
    SupportedGames: Game = Game.BL2
    SaveEnabledState: EnabledSaveType = EnabledSaveType.LoadWithSettings
    
    PercentSlider: Options.Slider
    def __init__(self):
        self.PercentSlider = Options.Slider(
        Caption = "Percent",
        Description = "Determinants the percent of Anarchy Stacks you keep",
        StartingValue = 50,
        MinValue = 0,
        MaxValue = 100,
        Increment = 1
        )
        self.Options = [self.PercentSlider]
        self.firstime = True # icant i swear i hate this fucking moding
        self.path = os.getcwd() + r"/Mods/KeepAnarchy/saved_stacks.txt"
    
    def get_anarchy_stacks(self) -> int: #function shamelessly stolen from Justin99's Speedrun Pratice Mod
        """Get stacks of anarchy from the attribute definition."""
        current_anarchy = str(FindObject("DesignerAttributeDefinition", "GD_Tulip_Mechromancer_Skills.Misc.Att_Anarchy_NumberOfStacks").GetValue(cast(UObject, GetEngine().GamePlayers[0].Actor)))
        current_anarchy = current_anarchy[1:current_anarchy.find(".")]
        return int(current_anarchy)
    
    def set_anarchy_stacks(self, target_stacks) -> None: #function shamelessly stolen from Justin99's Speedrun Pratice Mod
        """Set anarchy stacks to desired value""" 
        FindObject("DesignerAttributeDefinition", "GD_Tulip_Mechromancer_Skills.Misc.Att_Anarchy_NumberOfStacks").SetAttributeBaseValue(cast(UObject, GetEngine().GamePlayers[0].Actor), target_stacks)
    
    def save_anarchy_stacks(self) -> int:
        """Saves the current Anarchy to a textfile"""
        current_anarchy = self.get_anarchy_stacks()
        if current_anarchy != 0:
            with open(self.path, 'w') as stacks:
                stacks.write(str(int(current_anarchy)*self.PercentSlider.CurrentValue // 100))
    
    def retrive_anarchy_stacks(self) -> int:
        """Sets the current Anarchy to the Value that is saved in the textfile"""
        with open(self.path, 'r') as stacks:
            anarchy_stacks = stacks.read()
        with open(self.path, 'w') as stacks:
            stacks.write('')
        if len(anarchy_stacks) > 0:
            self.set_anarchy_stacks(int(anarchy_stacks))
    
    
    """Hooks that are used to determine when the player spawned for the first time after save quiting"""
    # cursed but it works
    @Hook("WillowGame.WillowPlayerController.SaveGame")
    def Spawned(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        if self.firstime:
            try:
                #Log("spawned")
                self.retrive_anarchy_stacks()
            except:
                Log("well fuck me")
                pass
            self.firstime = False
        return True
    
    @Hook("WillowGame.WillowPlayerController.SpawningProcessComplete")
    def onSpawn(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        self.firstime = True
        return True
    
    """Hook for detecting savequit and saving the Anarchystacks before"""
    @Hook("WillowGame.WillowPlayerController.ReturnToTitleScreen")
    def Spawn(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        try:
            self.save_anarchy_stacks()
        except:
            Log("didn't save the anarchy")
        #Log("quitting")
        return True
    
instance = anarchystacks()

if __name__ == "__main__":
    Log(f"[{instance.Name}] Manually loaded")
    for mod in Mods:
        if mod.Name == instance.Name:
            if mod.IsEnabled:
                mod.Disable()
            Mods.remove(mod)
            Log(f"[{instance.Name}] Removed last instance")

            # Fixes inspect.getfile()
            instance.__class__.__module__ = mod.__class__.__module__
            break

RegisterMod(instance)
