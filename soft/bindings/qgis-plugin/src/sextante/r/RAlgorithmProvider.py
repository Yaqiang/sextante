from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os.path
from sextante.script.WrongScriptException import WrongScriptException
from sextante.core.SextanteConfig import SextanteConfig, Setting
from sextante.core.SextanteLog import SextanteLog
from sextante.core.AlgorithmProvider import AlgorithmProvider
from PyQt4 import QtGui
from sextante.r.RUtils import RUtils
from sextante.r.RAlgorithm import RAlgorithm
from sextante.r.CreateNewRScriptAction import CreateNewRScriptAction
from sextante.r.EditRScriptAction import EditRScriptAction

class RAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        SextanteConfig.addSetting(Setting("R", RUtils.RSCRIPTS_FOLDER, "R Scripts folder", RUtils.RScriptsFolder()))
        SextanteConfig.addSetting(Setting("R", RUtils.R_FOLDER, "R folder", RUtils.RFolder()))
        self.actions = []
        self.actions.append(CreateNewRScriptAction())
        self.contextMenuActions = [EditRScriptAction()]

    def getIcon(self):
        return QtGui.QIcon(os.path.dirname(__file__) + "/../images/r.png")

    def getName(self):
        return "R"

    def _loadAlgorithms(self):
        folder = RUtils.RScriptsFolder()
        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith("rsx"):
                try:
                    fullpath = os.path.join(RUtils.RScriptsFolder(), descriptionFile)
                    alg = RAlgorithm(fullpath)
                    if alg.name.strip() != "":
                        alg.provider = self
                        self.algs.append(alg)
                except WrongScriptException,e:
                    SextanteLog.addToLog(SextanteLog.LOG_ERROR,e.msg)


