from pdfminer.layout import LTTextContainer
from pdfminer.layout import LTAnon


class LTTextWordsHorizontal(LTTextContainer):
    def __init__(self):
        LTTextContainer.__init__(self)
        self.start_row = -1
        self.end_row = -1
        self.start_col = -1
        self.end_col = -1
        self.children = []
        self.father = None

    def combine(self, word):
        if len(self._objs) > 0 and self._objs[-1].get_text() != '-':
            self._objs.append(LTAnon(' '))
        for ch in word:
            if isinstance(ch, LTAnon):
                self._objs.append(LTAnon(' '))
            else:
                self.add(ch)
        self.start_row = min(self.start_row, word.start_row)
        self.end_row = max(self.end_row, word.end_row)
        self.start_col = min(self.start_col, word.start_col)
        self.end_col = max(self.end_col, word.end_col)
        self.children += word.children

    def get_fontsize(self):
        return self._objs[0].fontname



