from islandoraUtils import fileConverter as converter
from utils.commonFedora import *

""" ====== INGEST A SINGLE OBJECT ====== """
def createObjectFromFiles(fedora, config, objectData):
    """
    Create a fedora object containing all the data in objectData and more
    """

    for ds in [ "TIFF", "MODS" ]:
        # some error checking
        if not objectData['datastreams'][ds]:
            # broken object
            print("Object data is missing required datastream: %s" % ds)
            return False

    #objPid = fedora.getNextPID(config.fedoraNS)
    objPid = "hpitt:%s" % objectData['label']

    #extraNamespaces = { 'pageNS' : 'info:islandora/islandora-system:def/pageinfo#' }
    #extraRelationships = { fedora_relationships.rels_predicate('pageNS', 'isPageNumber') : str(idx+1) }

    if config.dryrun:
        return True

    # create the object (page)
    try:
        obj = addObjectToFedora(fedora, unicode("%s" % objectData['label']), objPid, objectData['parentPid'], objectData['contentModel'])
    except FedoraConnectionException, fcx:
        print("Connection error while trying to add fedora object (%s) - the connection to fedora may be broken", page)
        return False

    # ingest the datastreams we were given
    for dsid, file in objectData['datastreams'].iteritems():
        # hard coded blarg:
        if dsid in ["MODS"]:
            controlGroup = "X"
        else:
            controlGroup = "M"
        fedoraLib.update_datastream(obj, dsid, file, label=unicode(os.path.basename(file)), mimeType=misc.getMimeType(os.path.splitext(file)[1]), controlGroup=controlGroup)
    #fedoraLib.update_datastream(obj, "TIFF", tifFile, label=unicode("%s.tif" % basePage), mimeType=misc.getMimeType("tiff"))

    # ingest my custom datastreams for this object
    # create a JPG datastream
    tifFile = objectData['datastreams']['TIFF']
    baseName = os.path.splitext(os.path.basename(tifFile))[0]
    jpgFile = os.path.join(config.tempDir, "%s.jpg" % baseName)
    converter.tif_to_jpg(tifFile, jpgFile, ['-compress', 'JPEG', '-quality', '90%']) # this will generate jpgFile
    fedoraLib.update_datastream(obj, u"JPG", jpgFile, label=unicode("%s.jpg" % baseName), mimeType=misc.getMimeType("jp2"))
    os.remove(jpgFile) # finished with that

    # ingest my custom datastreams for this object
    # create a JP2 datastream
    #tifFile = objectData['datastreams']['TIFF']
    #baseName = os.path.splitext(os.path.basename(tifFile))[0]
    #jp2File = os.path.join(config.tempDir, "%s.jp2" % baseName)
    #converter.tif_to_jp2(tifFile, jp2File, 'default', 'default') # this will generate jp2File
    #fedoraLib.update_datastream(obj, s"JP2", jp2File, label=unicode("%s.jp2" % baseName), mimeType=misc.getMimeType("jp2"))
    #os.remove(jp2File) # finished with that

    return True
