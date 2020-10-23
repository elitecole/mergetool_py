import os
import sys
import json
from collections import OrderedDict
import xmltodict

MERGE_FINISH_FILE_NAME = "mergefinish"

gAttrDef = {
    'Uniform' : ('datetime','ver','args','name','type'),
    'Add' : ('total','success','fail','checkfail','outoftime',
            'sndcnt','sndcntsuc','sndcntfail','rcvcnt','rcvcntsuc','rcvcntfail','sndsize','rcvsize','rcvsize',
            'sndsize')
}

gPrefix = "summary"
gDicts = []
gSummaryDict = OrderedDict()

class Summary(object):
    
    def __init__(self, resultDir = "./", fileIndex = 0, divide = 1):
        self.mResultDir = ""
        self.mFileIndex = 0
        self.mDivide = 0

        self.mResultDir = resultDir
        self.mFileIndex = int(fileIndex)
        self.mDivide = int(divide)

        if self.mFileIndex != 0:
            return 

        if self.mResultDir[-1] not in ['\\', '/']:
             self.mResultDir += "/"

        # Rename the first summary file from summary.xml to summary_0.xml
        tempFileName = self.mResultDir + gPrefix + ".xml"
        tempFileNameNew = self.mResultDir + gPrefix + "_0.xml"
        try:
            os.remove(tempFileNameNew)
        except:
            pass
        try:
            os.rename(tempFileName, tempFileNameNew)
        except:
            pass

        return

    # Load all xml src to dict(jason)
    def JasonToXml(self):
        for index in range(0, self.mDivide):
            srcFileName = "%s%s_%d.xml" % (self.mResultDir, gPrefix, index)
            try:
                xml_file = open(srcFileName, "r")
                xml_string = xml_file.read()
                json = xmltodict.parse(xml_string)
                gDicts.append(json)
                xml_file.close()
            except:
                return
        return

    def MergeList(self, lst, index, root):
        list_index = 0
        for item in lst:
            if (index == 0):
                root.append(OrderedDict())
            self.MergeDict(item, index, root[list_index])    
            list_index += 1    

    def MergeDict(self, dct, index, root):
        for k, v in dct.items():
            if type(v) is list:
                if (index == 0):
                    root[k] = list()
                self.MergeList(v, index, root[k])
            else:
                if (k in gAttrDef['Uniform']):
                    root[k] = v
                elif (k in gAttrDef['Add']):
                    if (index == 0):
                        root[k] = v
                    else:
                        root[k] = str(int(root[k]) + int(v))
                else:
                    if (index == 0):
                        root[k] = OrderedDict()
                    self.MergeDict(v, index, root[k])

    def MergeAll(self):
        gSummaryDict.clear()
        for index in range(0, len(gDicts)):
            root = gSummaryDict
            self.MergeDict(gDicts[index], index, root)

    def SaveXmlFile(self):
        xml_string = xmltodict.unparse(gSummaryDict)
        xml_summary_file = open(self.mResultDir + gPrefix + ".xml", "w")
        xml_summary_file.write(xml_string)
        xml_summary_file.flush()
        xml_summary_file.close()

    def MergeFinish(self):
        merge_finish_file = open(self.mResultDir + MERGE_FINISH_FILE_NAME, "w")
        merge_finish_file.flush()
        merge_finish_file.close()

# resultDir = "./", fileIndex = 0, divide = 1
if __name__ == "__main__":

    if len(sys.argv) == 1:
        print ("Info: mergetool.py used by comaidagent in Cobra.")
        print ("Ver: 0.1")
        print ("Format: python mergetool.py report_dir 0 report_count")
    else:
        summary = Summary(sys.argv[1], sys.argv[2], sys.argv[3])

        summary.JasonToXml()
        summary.MergeAll()

        summary.SaveXmlFile()
        summary.MergeFinish()

    sys.exit(0)