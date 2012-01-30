from utils.commonFedora import *
import glob
import FileIngester

""" ====== INGEST FILES IN A FOLDER ====== """
def processFolder(fedora, config):
    """
    Create a bunch of fedora objects (1 for each tif in @config.inDir)
    """

    folder = config.inDir

    # first make sure folder is a valid folder
    if not os.path.isdir(folder):
        return False

    # the collection overhead
    # the host collection (topmost root)
    hostCollection = addCollectionToFedora(fedora, config.hostCollectionName, myPid=config.hostCollectionPid, tnUrl=config.hostCollectionIcon)
    # the aggregate (image root)
    myCollection = addCollectionToFedora(fedora, config.myCollectionName, myPid=config.myCollectionPid, parentPid=config.hostCollectionPid, tnUrl=config.myCollectionIcon)

    # this is the list of all folders to search in for images
    baseFileDict = { 'parentPid' : config.myCollectionPid, 'contentModel' : 'islandora:sp_large_image_cmodel' }
    totalFiles = 0
    completeFiles = 0
    for subFolder in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, subFolder)):
            print("Scan Folder %s" % subFolder)
            fileDict = { 'label': subFolder, 'datastreams' : { } }

            def addFileByPattern(label, pattern):
                file = glob.glob("%s" % os.path.join(folder, subFolder, pattern))
                if len(file) > 0:
                    fileDict['datastreams'][label] = file[0]
                    return True
                return False

            if not addFileByPattern("TIFF", "*.tif"):
                if not addFileByPattern("TIFF", "*.tiff"):
                    # failed
                    print("Could not find base tif file - skipping directory")
                    continue # next subFolder
            addFileByPattern("MODS", "*.mods.xml")
            addFileByPattern("TN", "*.thumb.jpg")
            addFileByPattern("DC", "*.dc.xml")

            # creation of the dictionary here might be bad
            fileDict.update(baseFileDict)
            totalFiles = totalFiles + 1
            if FileIngester.createObjectFromFiles(fedora, config, fileDict):
                print("Object (%s) ingested successfully" % subFolder)
                completeFiles = completeFiles + 1

    """
    for idx, page in enumerate(pages):
        print("\n==========\nIngesting object %d of %d: %s" % (idx+1, count, page))

        if not config.dryrun:
            basePage = os.path.splitext(os.path.basename(page))[0]

            #pagePid = fedora.getNextPID(config.fedoraNS)
            pagePid = "%s-%d" % (bookPid, idx+1)
            # pageCModel doesn't exist - its just here as a placeholder

            extraNamespaces = { 'pageNS' : 'info:islandora/islandora-system:def/pageinfo#' }
            extraRelationships = { fedora_relationships.rels_predicate('pageNS', 'isPageNumber') : str(idx+1) }

            # ingest the tiff
            tifFile = os.path.join(folder, page)
            fedoraLib.update_datastream(obj, "TIFF", tifFile, label=unicode("%s.tif" % basePage), mimeType=misc.getMimeType("tiff"))

            # create a JP2 datastream
            jp2File = os.path.join(config.tempDir, "%s.jp2" % basePage)

            # ingest the ocr if it exists
            if ocrzip:
                # try to find the files' ocr data
                ocrFileName = "%s.txt" % basePage
                if ocrFileName in ocrzip.namelist():
                    ocrFile = ocrzip.extract(ocrFileName, config.tempDir)
                    fedoraLib.update_datastream(obj, "OCR", os.path.join(config.tempDir, ocrFile), label=unicode(ocrFileName), mimeType=misc.getMimeType("txt"))

            os.remove(jp2File) # finished with that
            os.remove(os.path.join(config.tempDir, ocrFileName)) # get rid of that temp file

        sys.stdout.flush()
        sys.stderr.flush()
    """

    config.message.addLine("Ingested %d/%d objects" % (completeFiles, totalFiles))

    return True
