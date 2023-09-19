# importing filecmp module
import filecmp
import shutil
import os
import logging
import schedule
import time
from   os import path
import sys


def MySync(source,replica,logfilepath):
    # compare source and replica folders
    # https://docs.python.org/3/library/filecmp.html
    res = filecmp.dircmp(source, replica, ignore=None, hide=None)

    # get unique files in source
    sourceonly = res.left_only

    # get unique files in replica
    replicaonly = res.right_only

    # open log file
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', handlers=[logging.FileHandler(logfilepath), logging.StreamHandler()])
    logging.info("New job scheduled")


    # copy unique files in source
    for i in sourceonly:
        Full_Sourcefile_Path = source + "/" + str(i)
        Full_Replica_SubDir_Path = replica + "/" + str(i)
        if path.exists(Full_Sourcefile_Path):
            if path.isfile(Full_Sourcefile_Path):
                shutil.copy2(Full_Sourcefile_Path, replica)
                # log copy
                logging.info("copying file " + str(Full_Sourcefile_Path) + " to replica folder")
            elif path.isdir(Full_Sourcefile_Path):
                shutil.copytree(Full_Sourcefile_Path, Full_Replica_SubDir_Path)
                # log copy
                logging.info("copying sub dir " + str(Full_Sourcefile_Path) + " to replica folder")
        else:
            print("Error source file does not exist")


    # delete files present only in replica
    for x in replicaonly:
        Full_Replicafile_Path = replica + "/" + str(x)
        if path.exists(Full_Replicafile_Path):
            if path.isfile(Full_Replicafile_Path):
                os.remove(Full_Replicafile_Path)
                logging.info("deleting unique file " + str(Full_Replicafile_Path) + " in replica folder")
            elif path.isdir(Full_Replicafile_Path):
                shutil.rmtree(Full_Replicafile_Path)
                logging.info("deleting unique sub dir " + str(Full_Replicafile_Path) + " in replica folder")
        else:
            print("Error replica folder file does not exist")

    res = filecmp.dircmp(source, replica, ignore=None, hide=None)
    sourceonly = res.left_only
    replicaonly = res.right_only
    if (sourceonly != []) or (replicaonly != []):
        logging.critical("Sync failed " + " sourceonly = " + str(sourceonly) + " replicaonly = " + str(replicaonly))

def schedule_foldersyn(schedule_time, source_path,replica_path,logfile_path):
    schedule.every(schedule_time).seconds.do(MySync, source_path,replica_path,logfile_path)
    logging.getLogger('schedule').propagate = False
    # run task at start
    MySync(source_path, replica_path, logfile_path)
    while True:
        schedule.run_pending()
        time.sleep(1)

def main(argv):
    if len(argv) == 4:
        # valid number of arguments
        if not (argv[0].isnumeric()):
            print("The first argument has to be a number representing scheduled time in secs")
            quit()
        if not (path.isdir(argv[1])):
            print("The second argument has to be a valid path to the source directory. Hint: use / or \\\\")
            quit()
        if not (path.isdir(argv[2])):
            print("The third argument has to be a valid path to the replica directory. Hint: use / or \\\\")
            quit()
        if not (path.isfile(argv[3])):
            print("The fourth argument has to be a valid path to the log file. Hint: use / or \\\\")
            quit()

        schedule_time_inSec = int(argv[0])
        source_path = argv[1]
        replica_path = argv[2]
        logfile_path = argv[3]

        schedule_foldersyn(schedule_time_inSec, source_path, replica_path, logfile_path)
    else:
        print("Incorrect number of arguments")
        print("Please use the following format")
        print("Python TestTask_FolderSync.py %timeInSec %SourceDirPath %ReplicaDirPath %LogfilePath")
        print("Example = Python TestTask_FolderSync.py 30 C:/users/Source C:/Users/Replica C:/users/logfile.txt")

if __name__ == "__main__":
   main(sys.argv[1:])















