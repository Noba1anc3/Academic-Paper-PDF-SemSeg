class DEBUG:
    pass

class RUN:
    pass

class HALF:
    pass

class FULL:
    pass

class LTPageNo:
    pass

class LTNote:
    pass

class Title:
    pass

class Author:
    pass

class LTTitle(Title):
    def __init__(self):
        Title.__init__(self)

class LTAuthor(Author):
    def __init__(self):
        Author.__init__(self)