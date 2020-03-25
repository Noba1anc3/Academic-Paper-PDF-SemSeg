
import cv2
import numpy as np
from semseg.image.tools import IOU
from utils.readWrite.write import ImageWrite

def get_annonum(annotate):
    annonum = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
               'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0,
               'Table': 0, 'Cell': 0}
    annoarea = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0,
                'Table': 0, 'Cell': 0}

    for i in range(len(annotate.Anno)):
        anno = annotate.Anno[i]
        for j in range(len(anno)):
            annonum[anno[j].split(' ')[0]] += 1
            annoarea[anno[j].split(' ')[0]] += get_annoarea(anno[j])

    for key in annonum.keys():
        if annonum[key] == 0:
            annonum[key] = 'NaN'
        if annoarea[key] == 0:
            annoarea[key] = 'NaN'
    return annonum, annoarea


def get_annoarea(annoline):

    return (int(annoline.split(' ')[3]) - int(annoline.split(' ')[1])) \
           * (int(annoline.split(' ')[4]) - int(annoline.split(' ')[2]))


def get_boxarea(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def numcalculate(total, true, anno):

    p = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0, 'Note': 0.0, 'PageNo': 0.0,
         'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}
    r = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0, 'Note': 0.0, 'PageNo': 0.0,
         'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}
    f = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0, 'Note': 0.0, 'PageNo': 0.0,
         'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}

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
            r[key] = true[key] / float(value)
            if p[key] + r[key] > 0:
                f[key] = 2 * p[key] * r[key] / (p[key] + r[key])
            else:
                f[key] = 0

    return p, r, f


def areacalculate(total, prearea, recarea, anno):
    p = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0,
         'TableNote': 0.0, 'Note': 0.0, 'PageNo': 0.0, 'Figure': 0.0,
         'Table': 0.0, 'Cell': 0.0}
    r = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0,
         'TableNote': 0.0, 'Note': 0.0, 'PageNo': 0.0, 'Figure': 0.0,
         'Table': 0.0, 'Cell': 0.0}
    f = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0,
         'TableNote': 0.0, 'Note': 0.0, 'PageNo': 0.0, 'Figure': 0.0,
         'Table': 0.0, 'Cell': 0.0}

    for key, value in anno.items():
        if value == 'NaN':
            p[key] = 'NaN'
            r[key] = 'NaN'
            f[key] = 'NaN'
        else:
            if total[key] == 0:
                p[key] = 0.00
            else:
                p[key] = prearea[key] / total[key]
            r[key] = recarea[key] / float(value)
            if p[key] + r[key] > 0.0:
                f[key] = 2 * p[key] * r[key] / (p[key] + r[key])
            else:
                f[key] = 0.00

    return p, r, f


def estimate(PagesImage, segment, annotate, img_folder):
    Images = []
    annonum, annoarea = get_annonum(annotate)

    pdftotalnum = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                   'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0,
                   'Table': 0, 'Cell': 0}
    pdftruenum = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                  'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0,
                  'Table': 0, 'Cell': 0}
    pdftotalarea = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                    'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0,
                    'Table': 0, 'Cell': 0}
    pdfprearea = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                  'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0,
                  'Table': 0, 'Cell': 0}
    pdfrecarea = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                  'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0,
                  'Table': 0, 'Cell': 0}

    pages = segment['Pages']

    for pageindex in range(len(pages)):
        page = pages[pageindex]
        anno = annotate.Anno[pageindex]
        image = PagesImage[pageindex]
        layout = page['PageLayout']
        for key, value in layout[0].items():
            if key == 'Text':
                textlist = value
            elif key == 'Figure':
                figurelist = value
            else:
                tablelist = value

        semerror = []
        annofound = []
        anno_notfound = []

        # text
        for textindex in range(len(textlist)):
            threshold = False
            text = textlist[textindex]
            semtype = text['SemanticType']
            prebox = text['location']
            pdftotalnum[semtype] += 1
            prearea = get_boxarea(prebox)
            pdftotalarea[semtype] += prearea
            if semtype == 'Text':
                #semerror.append(text)
                pass
            else:
                for annoindex in range(len(anno)):
                    if anno[annoindex].split(' ')[0] == semtype:
                        anbox = []
                        for i in range(4):
                            anbox.append(int(anno[annoindex].split(' ')[i+1]))
                        Iou = IOU(prebox, anbox)
                        if Iou > 0.7 :
                            threshold = True
                            pdftruenum[semtype] += 1
                            pdfprearea[semtype] += prearea
                            pdfrecarea[semtype] += get_boxarea(anbox)
                            annofound.append(anno[annoindex])
                            break
                if not threshold:
                    semerror.append(text)

        # figure
        for figureindex in range(len(figurelist)):
            threshold = False
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
                        threshold = True
                        pdftruenum[semtype] += 1
                        pdfprearea[semtype] += prearea
                        pdfrecarea[semtype] += get_boxarea(anbox)
                        annofound.append(anno[annoindex])
                        break
            if not threshold:
                figure['SemanticType'] = semtype
                semerror.append(figure)

        # table
        for tableindex in range(len(tablelist)):
            threshold = False
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
                        threshold = True
                        pdftruenum[semtype] += 1
                        pdfprearea[semtype] += prearea
                        pdfrecarea[semtype] += get_boxarea(anbox)
                        annofound.append(anno[annoindex])
                        break
            if not threshold:
                table['SemanticType'] = semtype
                semerror.append(table)

            # Cell
            row_header = table['row_header']
            col_header = table['col_header']
            datalist = table['data']
            for headerindex in range(len(row_header)):     # row header
                threshold = False
                cell = row_header[headerindex]
                semtype = 'Cell'
                prebox = cell['location']
                pdftotalnum[semtype] += 1
                prearea = get_boxarea(prebox)
                pdftotalarea[semtype] += prearea
                for annoindex in range(len(anno)):
                    anbox = []
                    if anno[annoindex].split(' ')[0] == semtype:
                        for i in range(4):
                            anbox.append(int(anno[annoindex].split(' ')[i + 1]))
                        Iou = IOU(prebox, anbox)
                        if Iou > 0.5:
                            threshold = True
                            pdftruenum[semtype] += 1
                            pdfprearea[semtype] += prearea
                            pdfrecarea[semtype] += get_boxarea(anbox)
                            annofound.append(anno[annoindex])
                            break
                if not threshold:
                    cell['SemanticType'] = semtype
                    semerror.append(cell)

            for headerindex in range(len(col_header)):     # col header
                threshold = False
                cell = col_header[headerindex]
                semtype = 'Cell'
                prebox = cell['location']
                pdftotalnum[semtype] += 1
                prearea = get_boxarea(prebox)
                pdftotalarea[semtype] += prearea
                for annoindex in range(len(anno)):
                    anbox = []
                    if anno[annoindex].split(' ')[0] == semtype:
                        for i in range(4):
                            anbox.append(int(anno[annoindex].split(' ')[i + 1]))
                        Iou = IOU(prebox, anbox)
                        if Iou > 0.5:
                            threshold = True
                            pdftruenum[semtype] += 1
                            pdfprearea[semtype] += prearea
                            pdfrecarea[semtype] += get_boxarea(anbox)
                            annofound.append(anno[annoindex])
                            break
                if not threshold:
                    cell['SemanticType'] = semtype
                    semerror.append(cell)

            for dataindex in range(len(datalist)):     # data
                threshold = False
                cell = datalist[dataindex]
                semtype = 'Cell'
                prebox = cell['location']
                pdftotalnum[semtype] += 1
                prearea = get_boxarea(prebox)
                pdftotalarea[semtype] += prearea
                for annoindex in range(len(anno)):
                    anbox = []
                    if anno[annoindex].split(' ')[0] == semtype:
                        for i in range(4):
                            anbox.append(int(anno[annoindex].split(' ')[i + 1]))
                        Iou = IOU(prebox, anbox)
                        if Iou > 0.5:
                            threshold = True
                            pdftruenum[semtype] += 1
                            pdfprearea[semtype] += prearea
                            pdfrecarea[semtype] += get_boxarea(anbox)
                            annofound.append(anno[annoindex])
                            break
                if not threshold:
                    cell['SemanticType'] = semtype
                    semerror.append(cell)

        # annotation not found  and  segmentation error
        for i in range(len(anno)):
            if anno[i] not in annofound:
                anno_notfound.append(anno[i])

        if len(anno_notfound) + len(semerror) > 0:
            image = np.array(image)

            for i in range(len(anno_notfound)):
                error = anno_notfound[i]
                semtype = error.split(' ')[0]

                x1 = int(error.split(' ')[1])
                y1 = int(error.split(' ')[2])
                x2 = int(error.split(' ')[3])
                y2 = int(error.split(' ')[4])

                cv2.rectangle(image, (x1, y1), (x2, y2), (255, 140, 0), 3)
                cv2.putText(image, semtype, (x1, y1), 0, 1.5, (255, 140, 0), 2)

            for i in range(len(semerror)):
                error = semerror[i]
                semtype = error['SemanticType']

                x1 = error['location'][0]
                y1 = error['location'][1]
                x2 = error['location'][2]
                y2 = error['location'][3]

                cv2.rectangle(image, (x1, y1), (x2, y2), (122, 103, 238), 3)
                cv2.putText(image, semtype, (x1, y1), 0, 1.5, (122, 103, 238), 2)

                Images.append(image)
        else:
            Images.append(None)

    ImageWrite(Images, segment['FileName'], img_folder)

    p_num, r_num, f_num = numcalculate(pdftotalnum, pdftruenum, annonum)
    p_area, r_area, f_area = areacalculate(pdftotalarea, pdfprearea, pdfrecarea, annoarea)

    return p_num, r_num, f_num, p_area, r_area, f_area