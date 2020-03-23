import sys
from semseg.image.tools import IOU
sys.dont_write_bytecode = True


def get_Anno(annotate):
    annoNum = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
               'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}
    annoArea = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}

    for i in range(len(annotate.Anno)):
        anno = annotate.Anno[i]
        for j in range(len(anno)):
            annoNum[anno[j].split(' ')[0]] += 1
            annoArea[anno[j].split(' ')[0]] += get_annoarea(anno[j])

    for key in annoNum.keys():
        if annoNum[key] == 0:
            annoNum[key] = 'NaN'
        if annoArea[key] == 0:
            annoArea[key] = 'NaN'

    return annoNum, annoArea


def get_annoarea(annoline):

    return (int(annoline.split(' ')[3]) - int(annoline.split(' ')[1])) \
           * (int(annoline.split(' ')[4]) - int(annoline.split(' ')[2]))


def get_boxarea(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def numcalculate(total, true, anno):
    p = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
         'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}
    r = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
         'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}
    f = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
         'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}

    for key, value in anno.items():
        if value == 'NaN':
            p[key] = 'NaN'
            r[key] = 'NaN'
            f[key] = 'NaN'
        else:
            if total[key] == 0:
                p[key] = 0
            else:                 
                p[key] = true[key] / total[key]

            r[key] = true[key] / value

            if p[key] + r[key] > 0:
                f[key] = 2 * p[key] * r[key] / (p[key] + r[key])
            else:
                f[key] = 0

    return p, r, f


def areacalculate(total, prearea, recarea, anno):
    p = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
         'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}
    r = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
         'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}
    f = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
         'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}

    for key, value in anno.items():
        if value == 'NaN':
            p[key] = 'NaN'
            r[key] = 'NaN'
            f[key] = 'NaN'
        else:
            if total[key] == 0:
                p[key] = 0
            else:
                p[key] = prearea[key] / total[key]

            r[key] = recarea[key] / value

            if p[key] + r[key] > 0:
                f[key] = 2 * p[key] * r[key] / (p[key] + r[key])
            else:
                f[key] = 0

    return p, r, f


def estimate(segment, annotate):
    annoNum, annoArea = get_Anno(annotate)
    
    pdftotalnum = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0, 'TableNote': 0, 'Note': 0, 'PageNo': 0,
                   'Figure': 0, 'Table': 0, 'Cell': 0}
    pdftruenum = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0, 'TableNote': 0, 'Note': 0, 'PageNo': 0,
                  'Figure': 0, 'Table': 0, 'Cell': 0}
    pdftotalarea = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0, 'TableNote': 0, 'Note': 0, 'PageNo': 0,
                    'Figure': 0, 'Table': 0, 'Cell': 0}
    pdfprearea = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0, 'TableNote': 0, 'Note': 0, 'PageNo': 0,
                  'Figure': 0, 'Table': 0, 'Cell': 0}
    pdfrecarea = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0, 'TableNote': 0, 'Note': 0, 'PageNo': 0,
                  'Figure': 0, 'Table': 0, 'Cell': 0}

    pages = segment['Pages']
    for pageindex in range(len(pages)):
        page = pages[pageindex]
        anno = annotate.Anno[pageindex]
        layout = page['PageLayout']
        for key, value in layout[0].items():
            if key == 'Text':
                textlist = value
            elif key == 'Figure':
                figurelist = value
            else:
                tablelist = value

        # text
        for textindex in range(len(textlist)):
            text = textlist[textindex]
            semtype = text['SemanticType']
            prebox = text['location']
            pdftotalnum[semtype] += 1
            prearea = get_boxarea(prebox)
            pdftotalarea[semtype] += prearea
            if semtype == 'Text':
                pass
            else:
                for annoindex in range(len(anno)):
                    if anno[annoindex].split(' ')[0] == semtype:
                        anbox = []
                        for i in range(4):
                            anbox.append(int(anno[annoindex].split(' ')[i+1]))
                        Iou = IOU(prebox, anbox)
                        if Iou > 0.7 or (Iou > 0.5 and semtype == 'PageNo'):
                            pdftruenum[semtype] += 1
                            pdfprearea[semtype] += prearea
                            pdfrecarea[semtype] += get_boxarea(anbox)
                            break

        # figure
        for figureindex in range(len(figurelist)):
            figure = figurelist[figureindex]
            semtype = 'Figure'
            prebox = figure['location']
            pdftotalnum[semtype] += 1
            prearea = get_boxarea(prebox)
            pdftotalarea[semtype] += prearea
            for annoindex in range(len(anno)):
                if anno[annoindex].split(' ')[0] == semtype:
                    anbox = []
                    for i in range(4):
                        anbox.append(int(anno[annoindex].split(' ')[i + 1]))
                    Iou = IOU(prebox, anbox)
                    if Iou > 0.8:
                        pdftruenum[semtype] += 1
                        pdfprearea[semtype] += prearea
                        pdfrecarea[semtype] += get_boxarea(anbox)
                        break

        # table
        for tableindex in range(len(tablelist)):
            table = tablelist[tableindex]
            semtype = 'Table'
            prebox = table['location']
            pdftotalnum[semtype] += 1
            prearea = get_boxarea(prebox)
            pdftotalarea[semtype] += prearea
            for annoindex in range(len(anno)):
                if anno[annoindex].split(' ')[0] == semtype:
                    anbox = []
                    for i in range(4):
                        anbox.append(int(anno[annoindex].split(' ')[i + 1]))
                    Iou = IOU(prebox, anbox)
                    if Iou > 0.8:
                        pdftruenum[semtype] += 1
                        pdfprearea[semtype] += prearea
                        pdfrecarea[semtype] += get_boxarea(anbox)
                        break

    p_num, r_num, f_num = numcalculate(pdftotalnum, pdftruenum, annoNum)
    p_area, r_area, f_area = areacalculate(pdftotalarea, pdfprearea, pdfrecarea, annoArea)

    return p_num, r_num, f_num, p_area, r_area, f_area
