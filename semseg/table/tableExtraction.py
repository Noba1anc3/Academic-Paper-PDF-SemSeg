from semseg.table.table_detection import detect_table
from semseg.table.table_structure_extraction import extraction
from semseg.table.cls import Region
from utils.logging.syslog import Logger
import sys

sys.dont_write_bytecode = True

class TableExtraction():
    def __init__(self, TableLevel, PagesLayout):
        self.Table = []
        self.Column_Header = []
        self.Row_Header = []
        self.Body = []
        self.TableLevel = TableLevel
        self.PagesLayout = PagesLayout
        self.Segmentation()

    def Segmentation(self):
        for PageLayout in self.PagesLayout:
            table = detect_table(PageLayout)

            newTable = []
            new_c_header = []
            new_r_header = []
            new_body = []

            for index in range(len(table)):
                tableItem = table[index]
                newTable.append(Region(tableItem))
                if self.TableLevel == 2:
                    c_header, r_header, body = extraction(PageLayout, tableItem)

                    for cell in c_header:
                        cell.insert(0, Region(cell[0]))
                        cell.remove(cell[1])
                    for cell in r_header:
                        cell.insert(0, Region(cell[0]))
                        cell.remove(cell[1])
                    for cell in body:
                        cell.insert(0, Region(cell[0]))
                        cell.remove(cell[1])

                    new_c_header.append(c_header)
                    new_r_header.append(r_header)
                    new_body.append(body)

            self.Table.append(newTable)
            if self.TableLevel == 2:
                self.Column_Header.append(new_c_header)
                self.Row_Header.append(new_r_header)
                self.Body.append(new_body)

        logging = Logger(__name__)
        Logger.get_log(logging).info('Table Segmentation Finished')
        logging.logger.handlers.clear()