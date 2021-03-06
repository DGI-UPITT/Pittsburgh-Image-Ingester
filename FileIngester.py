from islandoraUtils import fileConverter as converter
from utils.commonFedora import *
import subprocess

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
    objPid = "%s:%s" % (config.fedoraNS, objectData['label'])

    if config.dryrun:
        return True

    #extraNamespaces = { 'pageNS' : 'info:islandora/islandora-system:def/pageinfo#' }
    #extraRelationships = { fedora_relationships.rels_predicate('pageNS', 'isPageNumber') : str(idx+1) }

    # create the object (page)
    try:
        obj = addObjectToFedora(fedora, unicode("%s" % objectData['label']), objPid, objectData['parentPid'], objectData['contentModel'])
    except FedoraConnectionException, fcx:
        print("Connection error while trying to add fedora object (%s) - the connection to fedora may be broken", objPid)
        return False

    # ingest the datastreams we were given
    for dsid, file in objectData['datastreams'].iteritems():
        # hard coded blarg:
        if dsid in [ "MODS", "KML" ]:
            controlGroup = "X"
        else:
            controlGroup = "M"
        fedoraLib.update_datastream(obj, dsid, file, label=unicode(os.path.basename(file)), mimeType=misc.getMimeType(os.path.splitext(file)[1]), controlGroup=controlGroup)

    # ingest my custom datastreams for this object

    # create a JPG datastream
    #tifFile = objectData['datastreams']['TIFF']
    #baseName = os.path.splitext(os.path.basename(tifFile))[0]
    #jpgFile = os.path.join(config.tempDir, "%s.jpg" % baseName)
    #converter.tif_to_jpg(tifFile, jpgFile, ['-compress', 'JPEG', '-quality', '90%']) # this will generate jpgFile
    #fedoraLib.update_datastream(obj, u"JPG", jpgFile, label=unicode("%s.jpg" % baseName), mimeType=misc.getMimeType("jpg"))
    #os.remove(jpgFile) # finished with that

    # ingest my custom datastreams for this object
    # create a JP2 datastream
    tifFile = objectData['datastreams']['TIFF']
    baseName = os.path.splitext(os.path.basename(tifFile))[0]
    jp2File = os.path.join(config.tempDir, "%s.jp2" % baseName)
    converter.tif_to_jp2(tifFile, jp2File, 'default', 'default') # this will generate jp2File
    fedoraLib.update_datastream(obj, u"JP2", jp2File, label=os.path.basename(jp2File), mimeType=misc.getMimeType("jp2"))
    os.remove(jp2File) # finished with that

    # extract mix metadata
    #cmd= jhove -h xml $INFILE | xsltproc jhove2mix.xslt - > `basename ${$INFILE%.*}.mix`
    mixFile = os.path.join(config.tempDir, "%s.mix.xml" % baseName)
    """ extract this into tif_to_mix() """
    outfile = open(mixFile, "w")
    jhoveCmd1 = ["jhove", "-h", "xml", tifFile]
    jhoveCmd2 = ["xsltproc", "data/jhove2mix.xslt", "-"] # complete cmd for xsltproc
    #jhoveCmd2 = ["xalan", "-xsl", "data/jhove2mix.xslt"] # complete cmd for xalan
    p1 = subprocess.Popen(jhoveCmd1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(jhoveCmd2, stdin=p1.stdout, stdout=outfile)
    r = p2.communicate()
    if os.path.getsize(mixFile) == 0:
        # failed for some reason
        print("jhove conversion failed")
    outfile.close()
    """ end extract """
    fedoraLib.update_datastream(obj, u"MIX", mixFile, label=os.path.basename(mixFile), mimeType=misc.getMimeType("xml"))
    os.remove(mixFile)

    return True
