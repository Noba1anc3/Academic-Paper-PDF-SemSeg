
class Estimation():
    def __init__(self):
        self.total_pre_num = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'Note': 0.0,
                              'PageNo': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0,
                              'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}

        self.total_rec_num = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'Note': 0.0,
                              'PageNo': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0,
                              'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}

        self.total_f1_num = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'Note': 0.0,
                              'PageNo': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0,
                              'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}

        self.total_pre_area = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'Note': 0.0,
                              'PageNo': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0,
                              'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}

        self.total_rec_area = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'Note': 0.0,
                              'PageNo': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0,
                              'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}

        self.total_f1_area = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'Note': 0.0,
                              'PageNo': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0,
                              'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}

        self.valid_num = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'Note': 0.0,
                              'PageNo': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0,
                              'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}

    def num_add(self, prfList):
        pre_num = prfList[0]
        rec_num = prfList[1]
        f1_num = prfList[2]
        pre_area = prfList[3]
        rec_area = prfList[4]
        f1_area = prfList[5]

        for key in pre_num.keys():
            if pre_num[key] != 'NaN':
                self.valid_num[key] += 1

                self.total_pre_num[key]  += pre_num[key]
                self.total_rec_num[key]  += rec_num[key]
                self.total_f1_num[key]   += f1_num[key]

                self.total_pre_area[key] += pre_area[key]
                self.total_rec_area[key] += rec_area[key]
                self.total_f1_area[key]  += f1_area[key]

    def cal_total_score(self):
        for key in self.total_pre_num.keys():
            if self.valid_num[key] == 0:
                self.total_pre_num[key]  = 'NaN'
                self.total_rec_num[key]  = 'NaN'
                self.total_f1_num[key]   = 'NaN'
                self.total_pre_area[key] = 'NaN'
                self.total_rec_area[key] = 'NaN'
                self.total_f1_area[key]  = 'NaN'
            else:
                self.total_pre_num[key]  /= self.valid_num[key]
                self.total_rec_num[key]  /= self.valid_num[key]
                self.total_f1_num[key]   /= self.valid_num[key]
                self.total_pre_area[key] /= self.valid_num[key]
                self.total_rec_area[key] /= self.valid_num[key]
                self.total_f1_area[key]  /= self.valid_num[key]

        return [self.total_pre_num, self.total_rec_num, self.total_f1_num,
                self.total_pre_area, self.total_rec_area, self.total_f1_area]