from semseg.table.table_detection import detect_table
from semseg.table.cls import Region
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
        for PageLayout in self.PagesLayout:
            table = detect_table(PageLayout)
            newTable = []
            for index in range(len(table)):
                tableItem = table[index]
                newTable.append(Region(tableItem))
            self.Table.append(newTable)

        logging = Logger(__name__)
        Logger.get_log(logging).info('Table Segmentation Finished')
        logging.logger.handlers.clear()