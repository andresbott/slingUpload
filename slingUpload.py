#!/usr/bin/python2.7

import argparse
import os
import sys
import time

from libs.aemtools import aemtools
from libs.f import f
from libs.jsonfile import jsonfile

currentPath = os.getcwd()
projectConfigFile = "slingUpload.json"
projectConfigFileDefaults = {
    "rootFolder": "jcr_root",
    "server": "http://localhost:8080",
    "user": "admin",
    "pass": "admin",
}
mainConfig = jsonfile.jsonFile(currentPath + os.sep + projectConfigFile)

uploadList = ".SlingUploadFileList.json"
aemconnection = None
timestamp = None

def main(argv):
    parser = argparse.ArgumentParser(description='Upload / Download content to your Sling instance')
    group = parser.add_mutually_exclusive_group()
    # parser.add_argument('upload', metavar='upload',     help='run a backup job with the specified config file')
    group.add_argument("-u", "--upload", action="store_true", help='upload content')
    group.add_argument("-i", "--init", action="store_true", help='init repo')
    # parser.add_argument("-", "--quiet", action="store_true")
    # parser.add_argument('-restore', metavar='backupFile',   help='run a restore job with the specified backup file', type=argparse.FileType('r'))
    # parser.add_argument('-conffile', metavar='configFile',   help='specify a different restore config file', type=argparse.FileType('r'))
    # parser.add_argument('-restorefile', nargs=2 , metavar=('configFile','backupFile'),     help='run a restore job with the specified config file and the backupfile', type=argparse.FileType('r'))
    args = parser.parse_args()


    if mainConfig.fileExists():
        setneviroment()
        if args.upload is not False:
            upload()

        elif args.init is not False:
            print "This project is already configured."
            print "ignoring init"
            sys.exit(1)

        else:
            parser.print_help()
            sys.exit(1)

    else:
        if args.init is not False:
            print "init repo content"
            init()

        else:
            print "not Iit"
            parser.print_help()
            sys.exit(1)


def askinput(question,default=False):
    if default is not False:
        question = question + " (" + default + ") "
    else:
        question = question + ": "

    while True:
        inp = raw_input(question)
        if inp == "" and default is not False:
            inp = default
        if inp != "":
            return inp


def touch(path):
    """
     Create an empty file on the path if it does not exist
    """
    if not os.path.isfile(path):
        with open(path, 'a'):
            os.utime(path, None)


def init():
    """
     This function will initialize a FS repository:
        - create a configuration file for the repo
        - create the jcr_root directory
    """

    mainConfig.set("rootFolder",askinput("Name of your root dir: ",projectConfigFileDefaults["rootFolder"]))
    mainConfig.set("server",askinput("Url of your server: ",projectConfigFileDefaults["server"]))
    mainConfig.set("user",askinput("Server username: ",projectConfigFileDefaults["user"]))
    mainConfig.set("pass",askinput("Server password: ",projectConfigFileDefaults["pass"]))

    jcr_root = currentPath+os.sep+mainConfig.get("rootFolder")
    if not os.path.exists(jcr_root):
        os.makedirs(jcr_root)
    mainConfig.write()


def setneviroment():
    """
     this funtion does some pre run setttings:
       - will load the configuration file in the root directory (default file is slingUpload.json)
         this file contains configuration for the tool as alsto the connection data to connect to the sling / aem instance
       - create an AEMTools instance with the configuration details
       - set the timestamp for the current time

    """
    mainConfig.load()

    global aemconnection
    aemconnection = aemtools.AEMTools(mainConfig.get("server"), mainConfig.get("user"), mainConfig.get("pass"))

    global timestamp
    timestamp = int(time.time())



def upload():
    fileList = jsonfile.jsonFile(currentPath + os.sep + uploadList)
    # fileList.load()

    fileList.createSection("test")

    fileList.createSection(["files","subFiles"])
    fileList.createSection(["files","subFiles2"])
    fileList.createSection(["files","subFiles2","subFiles"])
    fileList.createSection(["dirs","subFiles2"])

    fileList.set("item","something") # done
    fileList.set("itemsa","something") # done
    fileList.set("itemsadas","something") # done
    fileList.set("dsa","something") # done
    fileList.set("dsads","something") # done
    fileList.set("item2","something",["dirs"]) #done
    fileList.set("item2","something","files") # done
    fileList.set("item3","something",["dirs","subFilesgfdgdf"])
    fileList.set("item34","something",["dirs","subFilesgfdgdf","subFilesgfdgdf"])
    fileList.set("item34","Value34",["dirs","subFilesgfdssdgdf","subFilesgfdgdf"])
    fileList.set("item35","Value35",["dirs","subFilesgfdssdgdf","subFilesgfdgdf"])

    fileList.set("item4",{"s":"b"},["dirs","subFiles2"])



    fileList.remove("item") # done
    fileList.remove("test") # done
    fileList.remove("item34",["dirs","subFilesgfdssdgdf","subFilesgfdgdf"])
    fileList.remove("subFilesgfdgdf",["dirs","subFilesgfdgdf"])

    print "whole json"
    print fileList.get()
    print "not existend string index:"
    print fileList.get("item")
    print "string index:"
    print fileList.get("dsads")
    print "LIST index return object:"
    print fileList.get(["dirs","subFilesgfdssdgdf","subFilesgfdgdf"])
    print "LIST index retunr string :"
    print fileList.get(["dirs","subFilesgfdssdgdf","subFilesgfdgdf","item35"])

    # print fileList.get("item")
    # print fileList.get(section = ["item"])
    # print fileList.get(section = ["files","subFiles2"])

    fileList.write()

    return
    if fileList.fileExists() is False:
        print "* Notice: Empty file list, generating new."

    repositoryPath = f.StringTools(currentPath + os.sep + mainConfig.get("rootFolder"))
    n = repositoryPath.countSting()

    # Create Dirs
    # ===================================================
    print "* Creating Direcotry structure:"
    # newUploadFiles["directories"] = []

    for root, dirs, files in os.walk(repositoryPath.get()):
        path = f.StringTools(root)
        path.stringRemoveLeft(n)
        path.trim()

        if path.get() is not "" and path.countSting() > 0:
            valuein = fileList.getValueIn("path", path.get(),"directories")

            if valuein is not False:
                print " - unchanged: "+path.get()
            else:
                status = aemconnection.createDir(path.get())
                if status["status"] ==  "ok":
                    print " - created:"+status["text"]
                    item = {
                        "path": path.get(),
                        "edittime": timestamp
                    }
                    fileList.set(value=item, section="directories")
                else:
                    print status["text"]



    # Create Files
    # ===================================================

    print "* Uploading Files to Repository:"
    fileList.createSection("files")

    for root, dirs, files in os.walk(repositoryPath.get()):
        path = f.StringTools(root)
        path.stringRemoveLeft(n)
        path.trim()

        if path.get() is not "" and path.countSting() > 0:
            if files:
                # File list is not empty
                for filename in files:
                    # absPAth = root + os.sep + filename
                    filepath = path.get() + os.sep +filename
                    localFile = repositoryPath.get() + filepath

                    valuein = fileList.getValueIn("path",filepath,"files")

                    if valuein is not False:
                        repoFileTime = int(valuein["edittime"])
                        fsFileTime = int(os.path.getmtime(root + os.sep + filename))

                        # print "repoTime:"+ str(repoFileTime) + " fs time: "+ str(fsFileTime)
                        if fsFileTime > repoFileTime:
                            # if FS time bigger (newer) we need to overwrite the Repo file
                            status = aemconnection.uploadFile(localFile, filepath)
                            if status["status"] == "ok":
                                print " - updated: " + status["text"]
                                item = {
                                    "path": filepath,
                                    "edittime": timestamp
                                }
                                fileList.set(value=item, section="files")
                            else:
                                print status["text"]
                        else:
                            print " - unchanged: " + filepath

                    else:
                        status = aemconnection.uploadFile(localFile,filepath)
                        if status["status"] ==  "ok":
                            print " - created: "+status["text"]
                            item = {
                                "path": filepath,
                                "edittime": timestamp
                            }
                            fileList.set(value=item, section="files")
                        else:
                            print status["text"]


    # Write changes to disk
    #===================================================

    fileList.write()









        # print os.path.basename(root)
        # print((len(path) - 1) * '---', os.path.basename(root))
        # for file in files:
        #     print(len(path) * '---', file)






        # print "upload: "+currentPath+"/"+projectConfigFile


    # echo "  * Creating Direcotry structure:"
    #
    # #     dirs=`find $DIR/$JRC_ROOT -type d`
    # basecount=`countString "$DIR/$JRC_ROOT"`
    #
    # find  "$DIR/$JRC_ROOT" -type d | while read myDir; do
    #     relative_path=`stringRemoveLeft "$myDir" $basecount`
    #     if [ ! -z "$relative_path" ]; then
    #         repocreateDir "$relative_path"
    #     fi
    # done




if __name__ == "__main__":
    main(sys.argv[1:])
