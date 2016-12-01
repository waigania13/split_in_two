# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SplitInTwo
                                 A QGIS plugin
 指定された属性を使って、割合にしたがつて２つに塗り分けます
                             -------------------
        begin                : 2016-11-30
        copyright            : (C) 2016 by mierune,llc.
        email                : waigania13@gmail.com
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SplitInTwo class from file SplitInTwo.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .split_intwo import SplitInTwo
    return SplitInTwo(iface)
