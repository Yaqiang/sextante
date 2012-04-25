from sextante.outputs.Output import Output
from sextante.parameters.Parameter import Parameter
from sextante.core.QGisLayers import QGisLayers
from sextante.parameters.ParameterRaster import ParameterRaster
from sextante.parameters.ParameterVector import ParameterVector
from PyQt4 import QtGui
import os.path
from sextante.core.SextanteUtils import SextanteUtils
from sextante.parameters.ParameterMultipleInput import ParameterMultipleInput
from sextante.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
import traceback
from sextante.core.SextanteLog import SextanteLog
from sextante.outputs.OutputVector import OutputVector
from sextante.outputs.OutputRaster import OutputRaster
from sextante.outputs.OutputTable import OutputTable
from sextante.outputs.OutputHTML import OutputHTML

class GeoAlgorithm:

    def __init__(self):
        #parameters needed by the algorithm
        self.parameters = list()
        #outputs generated by the algorithm
        self.outputs = list()
        self.name = ""
        self.group = ""
        #the crs taken from input layers (if possible), and used when loading output layers
        self.crs = None
        #change any of the following if your algorithm should not appear in the toolbox or modeler
        self.showInToolbox = True
        self.showInModeler = True
        #true if the algorithm has been canceled while it was being executed
        #default value is false, so it should be changed in processAlgorithm only if the algorithm
        #gets canceled
        self.canceled = False

        self.defineCharacteristics()

    #methods to overwrite when creating a custom geoalgorithm
    #=========================================================
    def getIcon(self):
        return QtGui.QIcon(os.path.dirname(__file__) + "/../images/alg.png")

    def helpFile(self):
        '''Returns the path to the help file with the description of this algorithm.
        It should be an HTML file'''
        return None

    def processAlgorithm(self):
        '''Here goes the algorithm itself
        There is no return value from this method. If the algorithm gets canceled
        while running this method, the self.canceled value should be set to false
        instead to indicate it.
        A GeoAlgorithmExecutionException should be raised in case something goes wrong.
        '''
        pass

    def defineCharacteristics(self):
        '''here is where the parameters and outputs should be defined'''
        pass

    def getCustomParametersDialog(self):
        '''if the algorithm has a custom parameters dialog, it should be returned
        here, ready to be executed'''
        return None

    def getCustomModelerParametersDialog(self, modelAlg):
        '''if the algorithm has a custom parameters dialog when called from the modeler,
        it should be returned here, ready to be executed'''
        return None

    def getParameterDescriptions(self):
        '''Returns a dict with param names as keys and detailed descriptions of each param
        as value. These descriptions are used as tool tips in the parameters dialog.
        If a description does not exist, the parameter's human-readable name is used'''
        descs = {}
        return descs

    def checkBeforeOpeningParametersDialog(self):
        '''If there is any check to perform before the parameters dialog is opened,
        it should be done here. This method returns an error message string if there
        is any problem (for instance, an external app not configured yet), or None
        if the parameters dialog can be opened.
        Note that this check should also be done in the processAlgorithm method,
        since algorithms can be called without opening the parameters dialog.'''
        return None

    def checkParameterValuesBeforeExecuting(self):
        '''If there is any check to do before launching the execution of the algorithm,
        it should be done here. If values are not correct, a message should be returned
        explaining the problem
        This check is called from the parameters dialog, and also when calling from the console'''
        return None
    #=========================================================

    def execute(self, progress):
        '''The method to use to call a SEXTANTE algorithm.
        Although the body of the algorithm is in processAlgorithm(),
        it should be called using this method, since it performs
        some additional operations.
        The return value indicates whether the algorithm was canceled (false)
        or successfully run (true).
        Raises a GeoAlgorithmExecutionException in case anything goes wrong.'''
        self.setOutputCRSFromInputLayers()
        self.resolveTemporaryOutputs()
        self.checkOutputFileExtensions()
        try:
            self.processAlgorithm(progress)
            return not self.canceled
        except GeoAlgorithmExecutionException, gaee:
            SextanteLog.addToLog(SextanteLog.LOG_ERROR, gaee.msg)
            raise gaee
        except Exception, e:
            #if something goes wrong and is not caught in the algorithm,
            #we catch it here and wrap it
            lines = []
            lines.append(str(e))
            lines.append(traceback.format_exc().replace("\n", "|"))
            SextanteLog.addToLog(SextanteLog.LOG_ERROR, lines)
            raise GeoAlgorithmExecutionException(str(e))

    def checkOutputFileExtensions(self):
        '''Checks if the values of outputs are correct and have one of the supported output extensions.
        If not, it adds the first one of the supported extensions, which is assumed to be the default one'''
        for out in self.outputs:
            if (not out.hidden) and out.value != None:
                if isinstance(out, OutputRaster):
                    exts = self.provider.getSupportedOutputRasterLayerExtensions()
                elif isinstance(out, OutputVector):
                    exts = self.provider.getSupportedOutputVectorLayerExtensions()
                elif isinstance(out, OutputTable):
                    exts = self.provider.getSupportedOutputTableExtensions()
                elif isinstance(out, OutputHTML):
                    exts =["html", "htm"]
                else:
                    continue
                idx = out.value.rfind(".")
                if idx == -1:
                    out.value = out.value + "." + exts[0]
                else:
                    ext = out.value[idx + 1:]
                    if ext not in exts:
                        out.value = out.value + "." + exts[0]

    def resolveTemporaryOutputs(self):
        '''sets temporary outputs (output.value = None) with a temporary file instead'''
        for out in self.outputs:
            if (not out.hidden) and out.value == None:
                SextanteUtils.setTempOutput(out, self)

    def setOutputCRSFromInputLayers(self):
        layers = QGisLayers.getAllLayers()
        for param in self.parameters:
            if isinstance(param, (ParameterRaster, ParameterVector, ParameterMultipleInput)):
                if param.value:
                    inputlayers = param.value.split(";")
                    for inputlayer in inputlayers:
                        for layer in layers:
                            if layer.source() == inputlayer:
                                self.crs = layer.crs()
                                return


    def addOutput(self, output):
        #TODO: check that name does not exist
        if isinstance(output, Output):
            self.outputs.append(output)

    def addParameter(self, param):
        #TODO: check that name does not exist
        if isinstance(param, Parameter):
            self.parameters.append(param)

    def setParameterValue(self, paramName, value):
        for param in self.parameters:
            if param.name == paramName:
                return param.setValue(value)

    def setOutputValue(self, outputName, value):
        for out in self.outputs:
            if out.name == outputName:
                out.value = value

    def getVisibleOutputsCount(self):
        '''returns the number of non-hidden outputs'''
        i = 0;
        for out in self.outputs:
            if not out.hidden:
                i+=1
        return i;

    def getOutputValuesAsDictionary(self):
        d = {}
        for out in self.outputs:
            d[out.name] = out.value
        return d


    def __str__(self):
        s = "ALGORITHM: " + self.name + "\n"
        for param in self.parameters:
            s+=("\t" + str(param) + "\n")
        for out in self.outputs:
            if not out.hidden:
                s+=("\t" + str(out) + "\n")
        s+=("\n")
        return s


    def commandLineName(self):
        return self.provider.getName().lower().replace(" ", "") + ":" + self.name.lower().replace(" ", "").replace(",","")

    def removeOutputFromName(self, name):
        for out in self.outputs:
            if out.name == name:
                self.outputs.remove(out)

    def getOutputFromName(self, name):
        for out in self.outputs:
            if out.name == name:
                return out

    def getParameterFromName(self, name):
        for param in self.parameters:
            if param.name == name:
                return param

    def getParameterValue(self, name):
        for param in self.parameters:
            if param.name == name:
                return param.value
        return None

    def getOutputValue(self, name):
        for out in self.outputs:
            if out.name == name:
                return out.value
        return None

    def getAsCommand(self):
        '''Returns the command that would run this same algorithm from the console.
        Should return null if the algorithm can be run from the console.'''
        s="Sextante.runalg(\"" + self.commandLineName() + "\","
        for param in self.parameters:
            s+=param.getValueAsCommandLineParameter() + ","
        for out in self.outputs:
            if not out.hidden:
                s+=out.getValueAsCommandLineParameter() + ","
        s= s[:-1] + ")"
        return s
