"""
<plugin key="SwedenEnergyPrice" name="Energy prices in Sweden" author="jbn" version="0.0.1" externallink="https://github.com/j-b-n">
    <description>
        <br/>
        <h2>Energy prices in Sweden</h2><br/>
        <p>
          The energy prices is provided by:
          <a href="https://www.elprisetjustnu.se">Elpriset just nu.se</a>
        </p>


        <h2>Parameters</h2><br/>
        <ul style="list-style-type:square">
            <li>Region</li>
            <li>Debug - Debug setting.</li>
        </ul>
        <br/>
    </description>

    <params>

       <param field="Mode1" label="Region" width="150px">
             <options>
                <option label="SE1" value="SE1" default="false"/>
                <option label="SE2" value="SE2" default="false"/>
                <option label="SE3" value="SE3" default="true"/>
                <option label="SE4" value="SE4" default="false"/>
            </options>
        </param>

       <param field="Mode6" label="Debug" width="150px">
             <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Python" value="18"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

##
# Plugin
##
import DomoticzEx as Domoticz
from decimal import Decimal
import time
import os
from datetime import datetime, timedelta
import elprisetjustnu

class BasePlugin:

    def __init__(self):
        self.current_price_updated = False
        self.daily_prices_updated = False

    def onStart(self):
        global _plugin

        if Parameters["Mode1"] == '':
            Parameters["Mode1"] = 'SE1'

        if Parameters["Mode6"] == '':
            Parameters["Mode6"] = 0
        if Parameters["Mode6"] != "0":

            Domoticz.Debugging(int(Parameters["Mode6"]))
            Domoticz.Debug("onStart called")

        Domoticz.Heartbeat(30)

        self.unit = "Kr"
        self.folder = Parameters["HomeFolder"] + 'json/'
        self.price_zone = Parameters["Mode1"]

        Domoticz.Log("Energy region set to "+self.price_zone)

        if os.path.isfile(Parameters["HomeFolder"]+'/EnergyPrice.zip'):
            if 'EnergyPrice' not in Images:
                Domoticz.Image('EnergyPrice.zip').Create()
            self.ImageID = Images["EnergyPrice"].ID


        if (len(Devices) != 28):
            if "CurrentElectricityPrice" not in Devices:
                Domoticz.Unit(Name="Current Electricity Price",DeviceID="CurrentElectricityPrice",
                              Unit=1, Type=243, Subtype=31, Used=1, Image=(self.ImageID),
                              Options={'Custom':'0;'+self.unit}).Create()
            if "MinElectricityPrice" not in Devices:
                Domoticz.Unit(Name="Minimum Electricity Price",DeviceID="MinElectricityPrice",
                              Unit=1, Type=243, Subtype=31, Used=1,Image=self.ImageID,
                              Options={'Custom':'0;'+self.unit}).Create()
            if "MaxElectricityPrice" not in Devices:
                Domoticz.Unit(Name="Maximum Electricity Price",DeviceID="MaxElectricityPrice",
                              Unit=1, Type=243, Subtype=31, Used=1,Image=self.ImageID,
                              Options={'Custom':'0;'+self.unit}).Create()
            if "AvgElectricityPrice" not in Devices:
                Domoticz.Unit(Name="Average Electricity Price",DeviceID="AvgElectricityPrice",
                              Unit=1, Type=243, Subtype=31, Used=1,Image=self.ImageID,
                              Options={'Custom':'0;'+self.unit}).Create()
            for hour in range(24):
                if "Hour"+str(hour)+"-ElectricityPrice" not in Devices:
                    Domoticz.Unit(Name="Hour-"+str(hour)+" Electricity Price",DeviceID="Hour"+str(hour)+"-ElectricityPrice",
                                  Unit=1, Type=243, Subtype=31, Used=1, Image=self.ImageID,
                                  Options={'Custom':'0;'+self.unit}).Create()


        min_price = elprisetjustnu.get_min_energy_price(self.folder, self.price_zone)
        update_device("MinElectricityPrice", Unit=1, sValue=str(min_price), nValue=0)
        Domoticz.Log("Update minimum energy price to "+str(min_price)+" at plugin start")

        max_price = elprisetjustnu.get_max_energy_price(self.folder, self.price_zone)
        update_device("MaxElectricityPrice", Unit=1, sValue=str(max_price), nValue=0)
        Domoticz.Log("Update maximum energy price to "+str(max_price)+" at plugin start")

        avg_price = elprisetjustnu.get_avg_energy_price(self.folder, self.price_zone)
        update_device("AvgElectricityPrice", Unit=1, sValue=str(avg_price), nValue=0)
        Domoticz.Log("Update average energy price to "+str(avg_price)+" at plugin start")

        for hour in range(24):
            hour_price = elprisetjustnu.get_hour_energy_price(self.folder, self.price_zone, hour)
            update_device("Hour"+str(hour)+"-ElectricityPrice", Unit=1, sValue=str(hour_price), nValue=0)
            Domoticz.Log("Hour-"+str(hour)+" updated to "+str(hour_price)+" at plugin start")




    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        hour = (datetime.now().hour)
        minute = (datetime.now().minute)

        if hour == 0 and self.daily_prices_updated is False:
            min_price = elprisetjustnu.get_min_energy_price(self.folder, self.price_zone)
            update_device("MinElectricityPrice", Unit=1, sValue=str(min_price), nValue=0)
            Domoticz.Log("Update minimum energy price to "+str(min_price))

            max_price = elprisetjustnu.get_max_energy_price(self.folder, self.price_zone)
            update_device("MaxElectricityPrice", Unit=1, sValue=str(max_price), nValue=0)
            Domoticz.Log("Update maximum energy price to "+str(max_price))

            avg_price = elprisetjustnu.get_avg_energy_price(self.folder, self.price_zone)
            update_device("AvgElectricityPrice", Unit=1, sValue=str(avg_price), nValue=0)
            Domoticz.Log("Update average energy price to "+str(avg_price))

            self.daily_prices_updated = True


        if minute < 59 and self.current_price_updated is False:
            current_price = elprisetjustnu.get_current_energy_price(self.folder, self.price_zone)
            update_device("CurrentElectricityPrice", Unit=1, sValue=str(current_price), nValue=0)
            Domoticz.Log("Update current energy price to "+str(current_price))
            self.current_price_updated = True

        if minute == 59 and self.current_price_updated is True:
            self.current_price_updated = False
            if hour == 23:
                self.daily_prices_updated = False

    def onStop(self):
        Domoticz.Log("onStop called")


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

####
## Generic helper functions
####


def update_device(ID, Unit = 1, sValue= 0, nValue = 0, TimedOut = 0, AlwaysUpdate = 0):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if Devices is not None and ID in Devices:
        if str(Devices[ID].Units[Unit].sValue) != str(sValue) or str(Devices[ID].Units[Unit].nValue) != str(nValue) or str(Devices[ID].TimedOut) != str(TimedOut) or AlwaysUpdate == 1:
            if sValue == None:
                sValue = Devices[ID].Units[Unit].sValue
            Devices[ID].Units[Unit].sValue = str(sValue)
            if type(sValue) == int or type(sValue) == float:
                Devices[ID].Units[Unit].LastLevel = sValue
            elif type(sValue) == dict:
                Devices[ID].Units[Unit].Color = json.dumps(sValue)
            Devices[ID].Units[Unit].nValue = nValue
            Devices[ID].TimedOut = TimedOut
            Devices[ID].Units[Unit].Update(Log=True)

            Domoticz.Debug('Update device value:' + str(ID) + ' Unit: ' + str(Unit) +
                           ' sValue: ' +  str(sValue) + ' nValue: ' + str(nValue) + ' TimedOut=' + str(TimedOut))
