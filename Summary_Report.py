# -------------------------------------------------------------------------------
# Name:        BRAT Validation
# Purpose:     Tests the output of BRAT against a shape file of beaver dams
#
# Author:      Braden Anderson
#
# Created:     05/2018
# -------------------------------------------------------------------------------

import os
import arcpy

def main(bratOutput, dams, outputName, layerPackageName):
    """
    The main function
    :param bratOutput: The output of BRAT (a polyline shapefile)
    :param dams: A shapefile containing a point for each dam
    :param outputName: The name of the output shape file
    :param layerPackageName: The name for the layer package
    :return:
    """
    arcpy.env.overwriteOutput = True
    if outputName.endswith('.shp'):
        outNetwork = os.path.join(os.path.dirname(bratOutput), outputName)
    else:
        outNetwork = os.path.join(os.path.dirname(bratOutput), outputName + ".shp")
    arcpy.Delete_management(outNetwork)

    damFields = ['e_DamCt', 'e_DamDens', 'e_DamPcC']
    otherFields = ['Ex_Categor', 'Pt_Categor', 'mCC_EX_Ct', 'mCC_PT_Ct', 'mCC_EXtoPT']
    newFields = damFields + otherFields

    inputFields = ['SHAPE@LENGTH', 'oCC_EX', 'oCC_PT']

    if dams:
        arcpy.AddMessage("Adding fields that need dam input...")
        setDamAttributes(bratOutput, outNetwork, dams, damFields + ['Join_Count'] + inputFields, newFields)
    else:
        arcpy.CopyFeatures_management(bratOutput, outNetwork)
        addFields(outNetwork, otherFields)

    arcpy.AddMessage("Adding fields that don't need dam input...")
    setOtherAttributes(outNetwork, otherFields + inputFields)

    if dams:
        cleanUpFields(bratOutput, outNetwork, newFields)

    makeLayers(outNetwork)
    makeLayerPackage(outNetwork, layerPackageName)


def setDamAttributes(bratOutput, outputPath, dams, reqFields, newFields):
    """
    Sets all the dam info and updates the output file with that data
    :param bratOutput: The polyline we're basing our stuff off of
    :param outputPath: The polyline shapefile with BRAT output
    :param dams: The points shapefile of observed dams
    :param damFields: The fields we want to update for dam attributes
    :return:
    """
    arcpy.Snap_edit(dams, [[bratOutput, 'EDGE', '30 Meters']])
    arcpy.SpatialJoin_analysis(bratOutput,
                               dams,
                               outputPath,
                               join_operation='JOIN_ONE_TO_ONE',
                               join_type='KEEP_ALL',
                               match_option='INTERSECT')
    addFields(outputPath, newFields)

    with arcpy.da.UpdateCursor(outputPath, reqFields) as cursor:
        for row in cursor:
            damNum = row[-4]        # fourth to last attribute
            segLength = row[-3]   # third to last attribute
            oCC_EX = row[-2]        # second to last attribute
            oCC_PT = row[-1]        # last attribute

            row[0] = damNum
            row[1] = damNum / segLength * 1000
            try:
                row[2] = damNum / oCC_PT
            except ZeroDivisionError:
                row[2] = 0

            cursor.updateRow(row)

    arcpy.DeleteField_management(outputPath, ["Join_Count", "TARGET_FID"])



def addFields(outputPath, newFields):
    """
    Adds the fields we want to our output shape file
    :param outputPath: Our output shape file
    :param newFields: All the fields we want to add
    :return:
    """
    textFields = ['Ex_Categor', 'Pt_Categor']
    for field in newFields:
        if field in textFields:
            arcpy.AddField_management(outputPath, field, field_type="TEXT", field_length=50)
        else: # we assume that the default is doubles
            arcpy.AddField_management(outputPath, field, field_type="DOUBLE", field_precision=0, field_scale=0)


def setOtherAttributes(outputPath, fields):
    """
    Sets the attributes of all other things we want to do
    :param outputPath: The polyline shapefile with BRAT output
    :param fields: The fields we want to update
    :return:
    """
    with arcpy.da.UpdateCursor(outputPath, fields) as cursor:
        for row in cursor:
            segLength = row[-3] # third to last attribute
            oCC_EX = row[-2] # second to last attribute
            oCC_PT = row[-1] # last attribute

            # Handles Ex_Categor
            row[0] = handleCategory(oCC_EX)

            # Handles Pt_Categor
            row[1] = handleCategory(oCC_PT)

            # Handles mCC_EX_Ct
            row[2] = (oCC_EX * segLength) / 1000

            # Handles mCC_PT_Ct
            row[3] = (oCC_PT * segLength) / 1000

            # Handles mCC_EXtoPT
            if oCC_PT != 0:
                row[4] = oCC_EX / oCC_PT
            else:
                row[4] = 0

            cursor.updateRow(row)


def handleCategory(oCCVariable):
    """
    Returns a string based on the oCC value given to it
    :param oCCVariable: A number
    :return: String
    """
    if oCCVariable == 0:
        return "None"
    elif 0 < oCCVariable <= 1:
        return "Rare"
    elif 1 < oCCVariable <= 5:
        return "Occasional"
    elif 5 < oCCVariable <= 15:
        return "Frequent"
    elif 15 < oCCVariable <= 40:
        return "Pervasive"
    else:
        return "UNDEFINED"


def cleanUpFields(bratNetwork, outNetwork, newFields):
    """
    Removes unnecessary fields
    :param bratNetwork: The original, unmodified stream network
    :param outNetwork: The output network
    :param newFields: All the fields we added
    :return:
    """
    originalFields = [field.baseName for field in arcpy.ListFields(bratNetwork)]
    desiredFields = originalFields + newFields
    outputFields = [field.baseName for field in arcpy.ListFields(outNetwork)]

    removeFields = []
    for field in outputFields:
        if field not in desiredFields:
            removeFields.append(field)

    if len(removeFields) > 0:
        arcpy.DeleteField_management(outNetwork, removeFields)


def makeLayers(out_network):
    """
    Writes the layers
    :param out_network: The output network, which we want to make into a layer
    :return:
    """
    arcpy.AddMessage("Making layers...")
    output_folder = os.path.dirname(out_network)

    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')
    conflictLayer = os.path.join(symbologyFolder, "Conflict.lyr")
    managementLayer = os.path.join(symbologyFolder, "Management_Zones.lyr")

    makeLayer(output_folder, out_network, "Conflict_Potential", conflictLayer, isRaster=False)
    makeLayer(output_folder, out_network, "Beaver_Management_Zones", managementLayer, isRaster=False)


def makeLayer(output_folder, layer_base, new_layer_name, symbology_layer, isRaster, description="Made Up Description"):
    """
    Creates a layer and applies a symbology to it
    :param output_folder: Where we want to put the folder
    :param layer_base: What we should base the layer off of
    :param new_layer_name: What the layer should be called
    :param symbology_layer: The symbology that we will import
    :param isRaster: Tells us if it's a raster or not
    :param description: The discription to give to the layer file
    :return: The path to the new layer
    """
    new_layer = new_layer_name + "_lyr"
    new_layer_save = os.path.join(output_folder, new_layer_name + ".lyr")

    if isRaster:
        arcpy.MakeRasterLayer_management(layer_base, new_layer)
    else:
        arcpy.MakeFeatureLayer_management(layer_base, new_layer)

    arcpy.ApplySymbologyFromLayer_management(new_layer, symbology_layer)
    arcpy.SaveToLayerFile_management(new_layer, new_layer_save)
    new_layer_instance = arcpy.mapping.Layer(new_layer_save)
    new_layer_instance.description = description
    new_layer_instance.save()
    return new_layer_save


def makeLayerPackage(outNetwork, layerPackageName):
    """
    Makes a layer package for the project
    :param outNetwork: The network in the fodler that we want to do stuff with.
    :param layerPackageName: The name of the layer package that we'll make
    :return:
    """
    if not layerPackageName.endswith(".lpk"):
        layerPackageName += ".lpk"

    arcpy.AddMessage("Making Layer Package...")
    analysesFolder = os.path.dirname(outNetwork)
    outputFolder = os.path.dirname(analysesFolder)
    intermediatesFolder = os.path.join(outputFolder, "01_Intermediates")
    projectFolder = os.path.dirname(outputFolder)
    inputsFolder = findFolder(projectFolder, "Inputs")

    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')
    emptyGroupLayer = os.path.join(symbologyFolder, "EmptyGroupLayer.lyr")

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]

    outputLayers = findLayersInFolder(analysesFolder)

    inputsLayer = getInputsLayer(emptyGroupLayer, inputsFolder, df, mxd)
    BRATLayer = groupLayers(emptyGroupLayer, "Beaver Restoration Assessment Tool - BRAT", outputLayers, df, mxd)
    intermediatesLayer = getIntermediatesLayer(emptyGroupLayer, intermediatesFolder, df, mxd)
    outputLayer = groupLayers(emptyGroupLayer, "Output", [BRATLayer, intermediatesLayer], df, mxd)
    outputLayer = groupLayers(emptyGroupLayer, layerPackageName[:-4], [outputLayer, inputsLayer], df, mxd, removeLayer=False)

    layerPackage = os.path.join(analysesFolder, layerPackageName)
    arcpy.PackageLayer_management(outputLayer, layerPackage)



def getInputsLayer(emptyGroupLayer, inputsFolder, df, mxd):
    """
    Gets all the input layers, groups them properly, returns the layer
    :param emptyGroupLayer: The base to build the group layer with
    :param inputsFolder: Path to the inputs folder
    :param df: The dataframe we're working with
    :param mxd: The map document we're working with
    :return: layer for inputs
    """
    vegetationFolder = findFolder(inputsFolder, "01_Vegetation")
    exVegFolder = findFolder(vegetationFolder, "01_ExistingVegetation")
    histVegFolder = findFolder(vegetationFolder, "02_HistoricVegetation")

    networkFolder = findFolder(inputsFolder, "02_Network")

    topoFolder = findFolder(inputsFolder, "03_Topography")

    conflictFolder = findFolder(inputsFolder, "04_Conflict")
    valleyFolder = findFolder(conflictFolder, "01_ValleyBottom")
    roadsFolder = findFolder(conflictFolder, "02_Roads")
    railroadsFolder = findFolder(conflictFolder, "03_Railroads")
    canalsFolder = findFolder(conflictFolder, "04_Canals")
    landUseFolder = findFolder(conflictFolder, "05_LandUse")

    exVegLayers = findInstanceLayers(exVegFolder)
    exVegLayer = groupLayers(emptyGroupLayer, "Existing_Vegetation_Type", exVegLayers, df, mxd)
    histVegLayers = findInstanceLayers(histVegFolder)
    histVegLayer = groupLayers(emptyGroupLayer, "Historic_Vegetation_Type", histVegLayers, df, mxd)
    vegLayer = groupLayers(emptyGroupLayer, "Vegetation", [exVegLayer, histVegLayer], df, mxd)

    networkLayers = findInstanceLayers(networkFolder)
    networkLayer = groupLayers(emptyGroupLayer, "Network", networkLayers, df, mxd)

    demLayers = findInstanceLayers(topoFolder)
    hillshadeLayers = find_dem_derivative(topoFolder, "Hillshade")
    slopeLayers = find_dem_derivative(topoFolder, "Slope")
    flowLayers = find_dem_derivative(topoFolder, "Flow")
    topoLayer = groupLayers(emptyGroupLayer, "Topography", demLayers + hillshadeLayers + slopeLayers + flowLayers, df, mxd)

    valleyLayers = findInstanceLayers(valleyFolder)
    valleyLayer = groupLayers(emptyGroupLayer, "Valley_Bottom", valleyLayers, df, mxd)
    roadLayers = findInstanceLayers(roadsFolder)
    roadLayer = groupLayers(emptyGroupLayer, "Roads", roadLayers, df, mxd)
    railroadLayers = findInstanceLayers(railroadsFolder)
    railroadLayer = groupLayers(emptyGroupLayer, "Railroads", railroadLayers, df, mxd)
    canalLayers = findInstanceLayers(canalsFolder)
    canalLayer = groupLayers(emptyGroupLayer, "Canals", canalLayers, df, mxd)
    landUseLayers = findInstanceLayers(landUseFolder)
    landUseLayer = groupLayers(emptyGroupLayer, "Land_Use", landUseLayers, df, mxd)
    conflictLayer = groupLayers(emptyGroupLayer, "Conflict_Layers", [valleyLayer, roadLayer, railroadLayer, canalLayer, landUseLayer], df, mxd)

    return groupLayers(emptyGroupLayer, "Inputs", [vegLayer, networkLayer, topoLayer, conflictLayer], df, mxd)


def getIntermediatesLayer(emptyGroupLayer, intermediatesFolder, df, mxd):
    """
    Returns a group layer with all of the intermediates
    :param emptyGroupLayer: The base to build the group layer with
    :param intermediatesFolder: Path to the intermediates folder
    :param df: The dataframe we're working with
    :param mxd: The map document we're working with
    :return: Layer for intermediates
    """
    buffers_folder = findFolder(intermediatesFolder, "01_Buffers")
    land_use_folder = findFolder(intermediatesFolder, "02_LandUse")
    topo_folder = findFolder(intermediatesFolder, "03_TopographicIndex")
    braid_folder = findFolder(intermediatesFolder, "04_BraidHandler")
    hydro_folder = findFolder(intermediatesFolder, "05_Hydrology")
    veg_folder = findFolder(intermediatesFolder, "06_VegCondition")

    buffer_layers = findLayersInFolder(buffers_folder)
    land_use_layers = findLayersInFolder(land_use_folder)
    topo_layers = findLayersInFolder(topo_folder)
    braid_layers = findLayersInFolder(braid_folder)
    hydro_layers = findLayersInFolder(hydro_folder)
    veg_layers = findLayersInFolder(veg_folder)

    intermediate_layers = []
    intermediate_layers.append(groupLayers(emptyGroupLayer, "Land_Use_Intensity", land_use_layers, df, mxd))
    intermediate_layers.append(groupLayers(emptyGroupLayer, "Buffers", buffer_layers, df, mxd))
    intermediate_layers.append(groupLayers(emptyGroupLayer, "Hydrology", hydro_layers, df, mxd))
    intermediate_layers.append(groupLayers(emptyGroupLayer, "Braid_Handler", braid_layers, df, mxd))
    intermediate_layers.append(groupLayers(emptyGroupLayer, "Overall_Vegetation_Condition", veg_layers, df, mxd))
    intermediate_layers.append(groupLayers(emptyGroupLayer, "Topographic_Index", topo_layers, df, mxd))

    return groupLayers(emptyGroupLayer, "Intermediates", intermediate_layers, df, mxd)


def findInstanceLayers(root_folder):
    """
    Finds every layer when buried beneath an additional layer of folders (ie, in DEM_1, DEM_2, DEM_3, etc)
    :param root_folder: The path to the folder root
    :return: A list of layers
    """
    layers = []
    for instance_folder in os.listdir(root_folder):
        instance_folder_path = os.path.join(root_folder, instance_folder)
        layers += findLayersInFolder(instance_folder_path)
    return layers


def find_dem_derivative(root_folder, dir_name):
    """
    Designed to look specifically for flow, slope, and hillshade layers
    :param root_folder: Where we look
    :param dir_name: The directory we're looking for
    :return:
    """
    layers = []
    for instance_folder in os.listdir(root_folder):
        instance_folder_path = os.path.join(os.path.join(root_folder, instance_folder), dir_name)
        layers += findLayersInFolder(instance_folder_path)
    return layers


def findLayersInFolder(folder_root):
    """
    Returns a list of all layers in a folder
    :param folder_root: Where we want to look
    :return:
    """
    layers = []
    for instance_file in os.listdir(folder_root):
        if instance_file.endswith(".lyr"):
            layers.append(os.path.join(folder_root, instance_file))
    return layers


def findFolder(folderLocation, folderName):
    """
    If the folder exists, returns it. Otherwise, raises an error
    :param folderLocation: Where to look
    :param folderName: The folder to look for
    :return: Path to folder
    """
    folder = os.path.join(folderLocation, folderName)
    if os.path.exists(folder):
        return folder
    else:
        raise Exception("The " + folderName + " folder does not exist, and so a layer package could not be created."
                        " It was supposed to be at the following location: \n" + folder)


def groupLayers(groupLayer, groupName, layers, df, mxd, removeLayer=True):
    """
    Groups a bunch of layers together
    :param groupLayer:
    :param groupName:
    :param layers:
    :param df:
    :param mxd:
    :param removeLayer: Tells us if we should remove the layer from the map display
    :return: The layer that we put our layers in
    """
    groupLayer = arcpy.mapping.Layer(groupLayer)
    groupLayer.name = groupName
    groupLayer.description = "Made Up Description"
    arcpy.mapping.AddLayer(df, groupLayer, "BOTTOM")
    groupLayer = arcpy.mapping.ListLayers(mxd, groupName, df)[0]

    for layer in layers:
        if not isinstance(layer, arcpy.mapping.Layer):
            layer_instance = arcpy.mapping.Layer(layer)
        else:
            layer_instance = layer
        arcpy.mapping.AddLayerToGroup(df, groupLayer, layer_instance)

    if removeLayer:
        arcpy.mapping.RemoveLayer(df, groupLayer)

    return groupLayer





