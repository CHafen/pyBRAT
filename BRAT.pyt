import os
import arcpy
import BRATProject
import BRAT_table
import iHyd
import Veg_FIS
import Comb_FIS
import Conflict_Potential
import Conservation_Restoration
import BRAT_Braid_Handler
import Summary_Report


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "BRAT Toolbox"
        self.alias = "BRAT Toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [BRAT_project_tool, BRAT_table_tool, BRAT_braid_handler, iHyd_tool, Veg_FIS_tool, Comb_FIS_tool, Conflict_Potential_tool, Conservation_Restoration_tool, Summary_Report_tool]


class BRAT_project_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 1. BRAT Project Builder"
        self.description = "Gathers inputs and creates folder structure for a BRAT project"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select project folder",
            name="projPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Select existing vegetation datasets",
            name="ex_veg",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param2 = arcpy.Parameter(
            displayName="Select historic vegetation datasets",
            name="hist_veg",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param3 = arcpy.Parameter(
            displayName="Select drainage network datasets",
            name="network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param4 = arcpy.Parameter(
            displayName="Select DEM inputs",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param5 = arcpy.Parameter(
            displayName="Select land use rasters",
            name="landuse",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param6 = arcpy.Parameter(
            displayName="Select valley bottom datasets",
            name="valley",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param7 = arcpy.Parameter(
            displayName="Select roads datasets",
            name="road",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param8 = arcpy.Parameter(
            displayName="Select railroads datasets",
            name="rr",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param9 = arcpy.Parameter(
            displayName="Select canals datasets",
            name="canal",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(BRATProject)
        BRATProject.main(p[0].valueAsText,
                        p[1].valueAsText,
                        p[2].valueAsText,
                        p[3].valueAsText,
                        p[4].valueAsText,
                        p[5].valueAsText,
                        p[6].valueAsText,
                        p[7].valueAsText,
                        p[8].valueAsText,
                        p[9].valueAsText)
        return


class BRAT_table_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 2. BRAT Table"
        self.description = "Calculates, for each stream network segment, the attributes needed to run the BRAT tools"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select project folder",
            name="projPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Project name",
            name="projName",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Watershed HUC ID",
            name="hucID",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName = "Watershed name",
            name="hucName",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Input segmented network",
            name="seg_network",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
        param4.filter.list = ["Polyline"]

        param5 = arcpy.Parameter(
            displayName="Input DEM",
            name="DEM",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="Input drainage area raster",
            name="FlowAcc",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input")

        param7 = arcpy.Parameter(
            displayName="Input coded existing vegetation raster",
            name="coded_veg",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param8 = arcpy.Parameter(
            displayName="Input coded historic vegetation raster",
            name="coded_hist",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param9 = arcpy.Parameter(
            displayName="Input valley bottom polygon",
            name="valley_bottom",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param9.filter.list = ["Polygon"]

        param10 = arcpy.Parameter(
            displayName="Input roads feature class",
            name="road",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param10.filter.list = ["Polyline"]

        param11 = arcpy.Parameter(
            displayName="Input railroads feature class",
            name="railroad",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param11.filter.list = ["Polyline"]

        param12 = arcpy.Parameter(
            displayName="Input canal feature class",
            name="canal",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param12.filter.list = ["Polyline"]

        param13 = arcpy.Parameter(
            displayName="Input landuse raster",
            name="landuse",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input")

        param14 = arcpy.Parameter(
            displayName="Name BRAT table output feature class",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param15 = arcpy.Parameter(
            displayName="Find Clusters",
            name="findClusters",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11, param12, param13, param14, param15]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(BRAT_table)
        BRAT_table.main(p[0].valueAsText,
                        p[1].valueAsText,
                        p[2].valueAsText,
                        p[3].valueAsText,
                        p[4].valueAsText,
                        p[5].valueAsText,
                        p[6].valueAsText,
                        p[7].valueAsText,
                        p[8].valueAsText,
                        p[9].valueAsText,
                        p[10].valueAsText,
                        p[11].valueAsText,
                        p[12].valueAsText,
                        p[13].valueAsText,
                        p[14].valueAsText,
                        p[15].valueAsText)
        return


class BRAT_braid_handler(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 3. BRAT Braid Handler (Optional)"
        self.description = "In development and currently non-operational. Gives braided streams the appropriate values, once mainstems have been identified in the stream network."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input BRAT network",
            name="inputNetwork",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        return [param0]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(BRAT_Braid_Handler)
        BRAT_Braid_Handler.main(p[0].valueAsText)
        return


class iHyd_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 4. iHyd Streamflow Attributes"
        self.description = "Calculates, for each stream network segment, discharge (in cubic meters per second) and stream power for both baseflow and annual peak streamflows"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input BRAT network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Polyline"]

        param1 = arcpy.Parameter(
            displayName="Select hydrologic region",
            name="region",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        return [param0, param1]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(iHyd)
        iHyd.main(p[0].valueAsText,
                  p[1].valueAsText)
        return

class Veg_FIS_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 5. BRAT Vegetation Dam Capacity Model"
        self.description = "Calculates dam capacity, for each stream network segment, based solely on vegetation.  Capacity is calculated separately for existing and potential (i.e., historic) vegetation type."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input BRAT network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Polyline"]

        return [param0]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(Veg_FIS)
        Veg_FIS.main(p[0].valueAsText)
        return

class Comb_FIS_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 6. BRAT Combined Dam Capacity Model"
        self.description = "Calculates dam capacity, for each stream network segment, based on vegetation dam capacity estimates, baseflow stream power, annual peak stream power, and slope.  Capacity is calculated separetly for existing and potential (i.e., history) vegetation."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select project folder",
            name="projPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Input BRAT network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName="Maximum DA threshold (in square kilometers)",
            name = "max_DA_thresh",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName = "Name combined capacity model output feature class",
            name = "out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        # param3.symbology = os.path.join(os.path.dirname(__file__), "Capacity.lyr")

        return [param0, param1, param2, param3]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(Comb_FIS)
        Comb_FIS.main(p[0].valueAsText,
                      p[1].valueAsText,
                      p[2].valueAsText,
                      p[3].valueAsText)
        return

class Conflict_Potential_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 7. BRAT Conflict Potential"
        self.description = "Calculates, for each stream network segment, the potential for human-beaver conflict based on landuse and distance from roads, railroads, canals.  Note: this tool can only be run if the user provides the conflict layers."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select project folder",
            name="projPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Select combined dam capacity output network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName="Input landuse raster",
            name="landuse",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Distance from road-stream crossing: LOW conflict threshold (in meters)",
            name = "CrossingLow",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param3.value = 10.0

        param4 = arcpy.Parameter(
            displayName="Distance from road-stream crossing: HIGH conflict threshold (in meters)",
            name = "CrossingHigh",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param4.value = 100.0

        param5 = arcpy.Parameter(
            displayName="Distance from road: LOW conflict threshold (in meters)",
            name = "AdjLow",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param5.value = 10.0

        param6 = arcpy.Parameter(
            displayName="Distance from road: HIGH conflict threshold (in meters)",
            name = "AdjHigh",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param6.value = 100.0

        param7 = arcpy.Parameter(
            displayName="Distance from canal: LOW conflict threshold (in meters)",
            name = "CanalLow",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param7.value = 50.0

        param8 = arcpy.Parameter(
            displayName="Distance from canal: HIGH conflict threshold (in meters)",
            name = "CanalHigh",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param8.value = 200.0

        param9 = arcpy.Parameter(
            displayName="Distance from railroad: LOW conflict threshold (in meters)",
            name = "RRLow",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param9.value = 30.0

        param10 = arcpy.Parameter(
            displayName="Distance from railroad: HIGH conflict threshold (in meters)",
            name = "RRHigh",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param10.value = 100.0

        param11 = arcpy.Parameter(
            displayName = "Name conflict potential model output network",
            name = "out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        # param11.symbology = os.path.join(os.path.dirname(__file__), "oPC.lyr")

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(Conflict_Potential)
        Conflict_Potential.main(p[0].valueAsText,
                                p[1].valueAsText,
                                p[2].valueAsText,
                                p[3].value,
                                p[4].value,
                                p[5].value,
                                p[6].value,
                                p[7].value,
                                p[8].value,
                                p[9].value,
                                p[10].value,
                                p[11].valueAsText)
        return

class Conservation_Restoration_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 8. BRAT Conservation and Restoration Model"
        self.description = "For each stream segment, assigns a conservation and restoration class based on existing dam capacity, potential (i.e., historic) dam capacity, and human-beaver conflict potential score"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select project folder",
            name="projPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Select conflict model output network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName="Name conservation restoration model output feature class",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        # param2.symbology = os.path.join(os.path.dirname(__file__), "oPBRC.lyr")

        return [param0, param1, param2]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(Conservation_Restoration)
        Conservation_Restoration.main(p[0].valueAsText,
                                      p[1].valueAsText,
                                      p[2].valueAsText)
        return

class Summary_Report_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 9. Summary Report"
        self.description = "Tests the results of BRAT against data on beaver dam sites"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Select conservation restoration model output network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Polyline"]

        param1 = arcpy.Parameter(
            displayName="Select beaver dam shape file",
            name="dams",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Name the validation shape file output",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        return [param0, param1, param2]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(Conservation_Restoration)
        Summary_Report.main(p[0].valueAsText,
                            p[1].valueAsText,
                            p[2].valueAsText)
        return