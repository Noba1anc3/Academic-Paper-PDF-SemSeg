from semseg.image.cls import Region as RegionCls
from semseg.image.tools import *
from pdfminer.layout import *

import sys
sys.dont_write_bytecode = True

def ImgExtraction(PageLayout, PageFNote):
    SemFig = []
    ImgFig = []
    Figure = []

    for FNote in PageFNote:
        # 图注之上的潜在区域搜索
        Region = potentialRegion(PageLayout, FNote)
        # 潜在区域紧缩
        Region = RegionContract(PageLayout, Region)
        # 边界交叉紧缩
        Region = BorderContract(PageLayout, Region)

        SemFig.append(Region)

    for Box in PageLayout:
        if isinstance(Box, LTFigure):
            Box = BorderContract(PageLayout, Box)
            ImgFig.append(Box)

    for SFig in SemFig:
        SFigLoc = [SFig.x0, PageLayout.height - SFig.y1, SFig.x1, PageLayout.height - SFig.y0]
        breakSign = False
        for IFig in ImgFig:
            IFigLoc = [IFig.x0, PageLayout.height - IFig.y1, IFig.x1, PageLayout.height - IFig.y0]
            iou = IOU(SFigLoc, IFigLoc)
            if iou > 0.5:
                Figure.append(IFig)
                breakSign = True
                ImgFig.remove(IFig)
                break
        if not breakSign:
            Figure.append(SFig)

    return Figure

def potentialRegion(PageLayout, FNote):
    Left = False
    Right = False

    PageWidth = PageLayout.width
    PageHeight = PageLayout.height

    FNoteYUp = PageHeight - FNote[0].y1

    if FNote[0].x1 * 2 < PageWidth:
        Left = True
    if FNote[0].x0 * 2 > PageWidth:
        Right = True

    RegionYDn = 0

    if Left or Right:
        for Box in PageLayout:
            if isinstance(Box, LTTextBoxHorizontal):
                # 横跨中央
                if Box.x0 * 2 < PageWidth and Box.x1 * 2 > PageWidth:
                    BoxYDn = PageHeight - Box.y0
                    if BoxYDn > RegionYDn and BoxYDn < FNoteYUp:
                        RegionYDn = BoxYDn
                # 左右两侧
                else:
                    # 各自寻找各自侧的Box
                    if Box.width * 3 > PageWidth:
                        if (Box.x1*2 < PageWidth and Left) or (Box.x0*2 > PageWidth and Right):
                            BoxYDn = PageHeight - Box.y0
                            if BoxYDn > RegionYDn and BoxYDn < FNoteYUp:
                                RegionYDn = BoxYDn

        if Left:
            location = [0, RegionYDn, PageWidth/2, FNoteYUp]
            return RegionCls(PageHeight, location)
        else:
            location = [PageWidth/2, RegionYDn, PageWidth, FNoteYUp]
            return RegionCls(PageHeight, location)

    else:
        for Box in PageLayout:
            if isinstance(Box, LTTextBoxHorizontal):
                BoxWidth = Box.width
                if BoxWidth * 3 > PageWidth:
                    BoxYDn = PageHeight - Box.y0
                    if BoxYDn > RegionYDn and BoxYDn < FNoteYUp:
                        RegionYDn = BoxYDn

        location = [0, RegionYDn, PageWidth, FNoteYUp]
        return RegionCls(PageHeight, location)

def RegionContract(PageLayout, Region):
    PgHeight = PageLayout.height
    PgWidth = PageLayout.width

    RegionXUp = Region.x0
    RegionYUp = PgHeight - Region.y1
    RegionXDn = Region.x1
    RegionYDn = PgHeight - Region.y0
    RegionLoc = [RegionXUp, RegionYUp, RegionXDn, RegionYDn]

    ContractXUp = PgWidth
    ContractYUp = PgHeight
    ContractXDn = 0
    ContractYDn = 0

    for Box in PageLayout:
        BoxXUp = Box.x0
        BoxYUp = PgHeight - Box.y1
        BoxXDn = Box.x1
        BoxYDn = PgHeight - Box.y0
        BoxLoc = [BoxXUp, BoxYUp, BoxXDn, BoxYDn]

        if BoxInsideCheck(RegionLoc, BoxLoc):
            if BoxXUp < ContractXUp:
                ContractXUp = BoxXUp
            if BoxYUp < ContractYUp:
                ContractYUp = BoxYUp
            if BoxXDn > ContractXDn:
                ContractXDn = BoxXDn
            if BoxYDn > ContractYDn:
                ContractYDn = BoxYDn

    if ContractXDn == 0:
        ContractLoc = RegionLoc
    else:
        ContractLoc = [ContractXUp, ContractYUp, ContractXDn, ContractYDn]

    return RegionCls(PgHeight, ContractLoc)

def BorderContract(PageLayout, Region):
    PgHeight = PageLayout.height

    RegionXUp = Region.x0
    RegionYUp = PgHeight - Region.y1
    RegionXDn = Region.x1
    RegionYDn = PgHeight - Region.y0
    RegionLoc = [RegionXUp, RegionYUp, RegionXDn, RegionYDn]

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal):
            BoxXUp = Box.x0
            BoxYUp = PgHeight - Box.y1
            BoxXDn = Box.x1
            BoxYDn = PgHeight - Box.y0
            BoxLoc = [BoxXUp, BoxYUp, BoxXDn, BoxYDn]

            if BoxInterCheck(RegionLoc, BoxLoc):
                if RegionYUp > BoxYUp and BoxYDn > RegionYUp:
                    RegionYUp = BoxYDn
                if RegionYDn < BoxYDn and BoxYUp < RegionYDn:
                    RegionYDn = BoxYUp

                RegionLoc = [RegionXUp, RegionYUp, RegionXDn, RegionYDn]

    return RegionCls(PgHeight, RegionLoc)
