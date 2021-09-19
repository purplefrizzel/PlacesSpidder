import datetime
import os


class Logger():

    def __init__(self) -> None:
        os.chdir("./")
        with open("logs/" + str(datetime.datetime.now().date()) + ".log", "a") as log:
            self.__logFile = log

    def info(self, msg):
        self.__log("info", msg)

    def error(self, msg):
        self.__log("error", msg)

    def verbose(self, msg):
        self.__log("verbose", msg)

    def __log(self, type: str, msg):
        print("[", type.capitalize(), "]", datetime.datetime.now(), "-", msg)

        if self.__logFile.closed != True:
            self.__logFile.writelines(
                "[" + type.capitalize() + "] " + str(datetime.datetime.now()) + " - " + msg + "\n")
        else:
            with open("logs/" + str(datetime.datetime.now().date()) + ".log", "a") as log:
                log.writelines(
                    "[" + type.capitalize() + "] " + str(datetime.datetime.now()) + " - " + msg + "\n")
