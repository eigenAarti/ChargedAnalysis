from task import Task

import os

class Plot1D(Task):
    def __init__(self, config = {}):
        super().__init__(config)

    def run(self):
        self["executable"] = "Plot1D"

        self["arguments"] = [
                self["hist-dir"], 
                "{}".format(" ".join(self["x-parameter"])),
                self["channel"], 
                "{}".format(" ".join(self["processes"])), 
                self["dir"], 
        ]

        super()._run()

    def output(self):
        self["output"] = ["{}/{}.pdf".format(self["dir"], x) for x in self["x-parameter"]]

    @staticmethod
    def configure(conf, haddTasks, channel):
        chanToDir = {"mu4j": "Muon4J", "e4j": "Ele4J", "mu2j1f": "Muon2J1F", "e2j1f": "Ele2J1F", "mu2f": "Muon2F", "e2f": "Ele2F"}
        
        tasks = []

        plotConf = {"name": "Plot_{}".format(channel), 
                    "channel": channel, 
                    "hist-dir": os.environ["CHDIR"] + "/Hist/{}/{}".format(conf[channel]["dir"], chanToDir[channel]), 
                    "dir":  os.environ["CHDIR"] + "/CernWebpage/Plots/{}/{}".format(conf[channel]["dir"], chanToDir[channel]), 
                    "display-name": "Plots: {}".format(channel), 
                    "x-parameter": conf[channel]["x-parameter"], 
                    "dependencies": [t["name"] for t in haddTasks if t["channel"] == channel], 
                    "processes": [t["process"] for t in haddTasks if t["channel"] == channel]
        }

        tasks.append(Plot1D(plotConf))

        return tasks
