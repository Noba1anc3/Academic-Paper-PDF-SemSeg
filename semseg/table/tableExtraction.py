from utils.logging.syslog import Logger
import sys
sys.dont_write_bytecode = True

class TableExtraction():
    def __init__(self, TableLevel, PagesLayout):
        self.Table = []
        self.TableLevel = TableLevel
        self.PagesLayout = PagesLayout
        self.Segmentation()

    def Segmentation(self):

        logging = Logger(__name__)
        Logger.get_log(logging).info('Table Segmentation Finished')
        logging.logger.handlers.clear()