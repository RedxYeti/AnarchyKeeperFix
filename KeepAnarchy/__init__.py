import unrealsdk
import os
from Mods.ModMenu import EnabledSaveType, Mods, ModTypes, RegisterMod, SDKMod, Options, Hook, Game
from typing import cast

from unrealsdk import FindObject, Log, UObject, GetEngine

class anarchystacks(SDKMod):
    Name: str = "KeepAnarchy"
    Author: str = "Sampletext282"
    Description: str = (
        "Lets you keep a user set percentage of your Anarchy stacks on Savequit."
    )
    Version: str = "0.1.1"
    Types: ModTypes = ModTypes.Utility
    SupportedGames: Game = Game.BL2
    SaveEnabledState: EnabledSaveType = EnabledSaveType.LoadWithSettings
    
    PercentSlider: Options.Slider
    Threshold: Options.Slider
    def __init__(self):
        self.PercentSlider = Options.Slider(
        Caption = "Keep%",
        Description = "The Percent of Anarchy stacks you keep.",
        StartingValue = 50,
        MinValue = 0,
        MaxValue = 100,
        Increment = 1
        )
        self.Threshold = Options.Slider(
        Caption = "Threshold",
        Description = "Anarchy stacks won't go below this Value. Leave at 0 to ignore.",
        StartingValue = 0,
        MinValue = 0,
        MaxValue = 600,
        Increment = 1
        )
        self.Options = [self.PercentSlider, self.Threshold]
        self.firstime = True # icant i swear i hate this fucking moding
        self.path = os.getcwd() + r"/Mods/KeepAnarchy/saved_stacks.txt"
    
    def get_anarchy_stacks(self) -> int: #function mostly stolen from Justin99's Speedrun Pratice Mod
        """Get stacks of anarchy from the attribute definition."""
        current_anarchy = str(FindObject("DesignerAttributeDefinition", "GD_Tulip_Mechromancer_Skills.Misc.Att_Anarchy_NumberOfStacks").GetValue(cast(UObject, GetEngine().GamePlayers[0].Actor)))
        current_anarchy = current_anarchy[1:current_anarchy.find(".")]
        return int(current_anarchy)
        
    def get_max_anarchy_stacks(self) -> int:
        max_anarchy = str(FindObject("DesignerAttributeDefinition", "GD_Tulip_Mechromancer_Skills.Misc.Att_Anarchy_StackCap").GetValue(cast(UObject, GetEngine().GamePlayers[0].Actor)))
        max_anarchy = max_anarchy[1:max_anarchy.find(".")]
        return int(max_anarchy)
    
    def set_anarchy_stacks(self, target_stacks) -> None: #function stolen from Justin99's Speedrun Pratice Mod
        """Set anarchy stacks to desired value""" 
        FindObject("DesignerAttributeDefinition", "GD_Tulip_Mechromancer_Skills.Misc.Att_Anarchy_NumberOfStacks").SetAttributeBaseValue(cast(UObject, GetEngine().GamePlayers[0].Actor), target_stacks)
        return
        
    def save_anarchy_stacks(self) -> int:
        """Saves the current Anarchy to a textfile"""
        current_anarchy = self.get_anarchy_stacks()
        if current_anarchy != 0:
            with open(self.path, 'w') as stacks:
                stacks.write(str(current_anarchy))
        return
        
    def retrive_anarchy_stacks(self) -> int:
        """Sets the current Anarchy to the Value that is saved in the textfile"""
        max_anarchy = self.get_max_anarchy_stacks()
        with open(self.path, 'r') as stacks:
            anarchy_stacks = stacks.read()
        if len(anarchy_stacks) > 0:
            anarchy_stacks = int(anarchy_stacks)
            if (anarchy_stacks*self.PercentSlider.CurrentValue // 100) >= self.Threshold.CurrentValue:
                self.set_anarchy_stacks(min(max_anarchy, anarchy_stacks*self.PercentSlider.CurrentValue // 100))
            elif anarchy_stacks > self.Threshold.CurrentValue:
                self.set_anarchy_stacks(min(max_anarchy,self.Threshold.CurrentValue))
            else:
                self.set_anarchy_stacks(min(max_anarchy,anarchy_stacks))
        with open(self.path, 'w') as stacks:
            stacks.write('')
        return
    
    """Hooks that are used to determine when the player spawned for the first time after save quiting"""
    # cursed but it works
    @Hook("WillowGame.WillowPlayerController.SaveGame")
    def Spawned(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        if self.firstime:
            try:
                Log("spawned")
                self.retrive_anarchy_stacks()
            except:
                Log("well fuck me")
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
