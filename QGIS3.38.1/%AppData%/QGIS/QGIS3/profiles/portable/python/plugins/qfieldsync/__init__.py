# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QFieldSync
                                 A QGIS plugin
 Sync your projects to QField on android
                             -------------------
        begin                : 2015-05-20
        copyright            : (C) 2015 by OPENGIS.ch
        email                : info@opengis.ch
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

from __future__ import absolute_import

import pathlib
import sys


src_dir = pathlib.Path(__file__).parent.resolve()

libqfieldsync_whl = src_dir / "libqfieldsync.whl"
if libqfieldsync_whl.exists():
    sys.path.append(str(libqfieldsync_whl))


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load QFieldSync class from file QFieldSync.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    from qfieldsync.qfield_sync import QFieldSync

    return QFieldSync(iface)
