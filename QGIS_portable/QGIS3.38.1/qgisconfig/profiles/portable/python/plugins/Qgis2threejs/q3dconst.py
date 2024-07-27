# -*- coding: utf-8 -*-
# (C) 2018 Minoru Akagi
# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import Qt


class LayerType:
    DEM = 0
    POINT = 1
    LINESTRING = 2
    POLYGON = 3
    POINTCLOUD = 4


class DEMMtlType:
    MAPCANVAS = 0
    LAYER = 1
    FILE = 2
    COLOR = 3

    ICON_PATH = {
        MAPCANVAS: "mLayoutItemMap.svg",
        LAYER: "algorithms/mAlgorithmMergeLayers.svg",
        FILE: "mLayoutItemPicture.svg"
    }


class Script:

    # Script ID
    PROJ4 = 1
    GLTFLOADER = 2
    COLLADALOADER = 3
    GLTFEXPORTER = 4
    POTREE = 5
    PCLAYER = 6
    OUTLINE = 7
    VIEWHELPER = 8
    MESHLINE = 9
    FETCH = 101
    TEST = 201

    # Script path (relative from js directory)
    PATH = {
        PROJ4: "proj4js/proj4.js",
        GLTFLOADER: "threejs/loaders/GLTFLoader.js",
        COLLADALOADER: "threejs/loaders/ColladaLoader.js",
        GLTFEXPORTER: "threejs/exporters/GLTFExporter.js",
        POTREE: "potree-core/potree.min.js",
        PCLAYER: "pointcloudlayer.js",
        OUTLINE: "threejs/effects/OutlineEffect.js",
        VIEWHELPER: "threejs/editor/ViewHelper.js",
        MESHLINE: "meshline/THREE.MeshLine.js",
        FETCH: "unfetch/unfetch.js",
        TEST: "../tests/gui/test.js"
    }


# Layer properties
GEOM_WIDGET_MAX_COUNT = 5
MTL_WIDGET_MAX_COUNT = 2        # excluding color, color2 and opacity


class PropertyID:

    ALT = 1
    ALT2 = 2

    PATH = 3

    G0 = 10
    G1 = 11
    G2 = 12
    G3 = 13
    G4 = 14

    C = 20
    C2 = 21
    OP = 22

    M0 = 23
    M1 = 24

    LBLH = 30
    LBLTXT = 31

    PID_NAME_DICT = {
        ALT: "fieldExpressionWidget_altitude",
        ALT2: "comboEdit_altitude2",
        PATH: "comboEdit_FilePath",
        C: "comboEdit_Color",
        C2: "comboEdit_Color2",
        OP: "comboEdit_Opacity",
        LBLH: "labelHeightWidget",
        LBLTXT: "expression_Label"
    }

    # animation
    DLY = 80
    DUR = 81

    ANIM_PID_NAME_DICT = {
        DLY: "delay",
        DUR: "duration"
    }

    @classmethod
    def init(cls):
        for i in range(GEOM_WIDGET_MAX_COUNT):
            cls.PID_NAME_DICT[cls.G0 + i] = "geomWidget" + str(i)

        for i in range(MTL_WIDGET_MAX_COUNT):
            cls.PID_NAME_DICT[cls.M0 + i] = "mtlWidget" + str(i)


PropertyID.init()


class ATConst:

    # ITEM TYPES

    # TOP LEVEL
    ITEM_TOPLEVEL = 32
    ITEM_TL_CAMERA = 32
    ITEM_TL_LAYER = 33

    # GROUP
    ITEM_GRP = 64

    ITEM_GRP_CAMERA = 64
    ITEM_GRP_OPACITY = 65
    ITEM_GRP_TEXTURE = 66
    ITEM_GRP_GROWING_LINE = 67

    # MEMBER OF GROUP (KEYFRAME OR EFFECT)
    ITEM_MBR = 128

    ITEM_CAMERA = 128
    ITEM_OPACITY = 129
    ITEM_TEXTURE = 130
    ITEM_GROWING_LINE = 131         # EFFECT

    # ITEM_TL_LAYER
    DATA_LAYER_ID = Qt.UserRole

    # KEYFRAME GROUP
    DATA_NEXT_INDEX = Qt.UserRole

    # COMMON FOR KEYFRAME
    DATA_EASING = Qt.UserRole + 1
    DATA_DURATION = Qt.UserRole + 2
    DATA_DELAY = Qt.UserRole + 3
    DATA_NARRATION = Qt.UserRole + 4

    # CAMERA KEYFRAME
    DATA_CAMERA = Qt.UserRole

    # OPACITY KEYFRAME
    DATA_OPACITY = Qt.UserRole

    # TEXTURE KEYFRAME
    DATA_MTL_ID = Qt.UserRole
    DATA_EFFECT = Qt.UserRole + 5

    # LINE GROWING EFFECT
    DATA_SEQ = Qt.UserRole

    # EASING
    EASING_NONE = 0
    EASING_LINEAR = 1
    EASING_EASE_INOUT = 2
    EASING_EASE_IN = 3
    EASING_EASE_OUT = 4

    @classmethod
    def defaultName(cls, typ):
        name = ["Camera", "Opacity", "Texture", "Growing line"]
        if typ & cls.ITEM_GRP:
            return "Group" if typ == cls.ITEM_GRP_CAMERA else "{} group".format(name[typ - cls.ITEM_GRP])

        if typ & cls.ITEM_MBR:
            return "{} keyframe".format(name[typ - cls.ITEM_MBR])

        return "UNDEF"
