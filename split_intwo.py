# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SplitInTwo
                                 A QGIS plugin
 指定された属性を使って、割合にしたがつて２つに塗り分けます
                              -------------------
        begin                : 2016-11-30
        git sha              : $Format:%H$
        copyright            : (C) 2016 by mierune,llc.
        email                : waigania13@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from split_intwo_dialog import SplitInTwoDialog
import os.path
from qgis.core import *
from qgis.utils import *


class SplitInTwo:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SplitInTwo_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = SplitInTwoDialog()
        self.dlg.buttonBox.accepted.connect(self.split)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Split in Two')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SplitInTwo')
        self.toolbar.setObjectName(u'SplitInTwo')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SplitInTwo', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SplitInTwo/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Split In Two'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Split in Two'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # clear combo box
        self.dlg.mMapLayerComboBox.clear() 
        self.dlg.mFieldComboBox.clear()
        # set layers
        layers = QgsMapLayerRegistry.instance().mapLayers()
        for id, layer in layers.iteritems():
            self.dlg.mMapLayerComboBox.setLayer(layer)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def split(self):
        layer = self.dlg.mMapLayerComboBox.currentLayer()
        field = self.dlg.mFieldComboBox.currentField()
        rate =  self.dlg.horizontalSlider.value()

        if field is None:
            return
   
        attr_values = []
        features = layer.getFeatures()
        for feature in features:
            attr_values.append(feature[field])

        target_value = sum(attr_values) * rate / 100.0
        attr_values.sort()
        attr_values.reverse()

        sum_value = 0.0
        for attr_value in attr_values:
            sum_value = sum_value + attr_value
            if sum_value >= target_value:
                value = attr_value
                break
             
        symbol1 = QgsSymbolV2.defaultSymbol(QGis.Polygon)
        fillLayer1 = QgsSimpleFillSymbolLayerV2(QColor(255, 0, 0), Qt.SolidPattern)
        symbol1.appendSymbolLayer(fillLayer1)
        symbol2 = QgsSymbolV2.defaultSymbol(QGis.Polygon)
        fillLayer2 = QgsSimpleFillSymbolLayerV2(QColor(0, 0, 255), Qt.SolidPattern)
        symbol2.appendSymbolLayer(fillLayer2)

        rule = QgsRuleBasedRendererV2.Rule(None)
        rule1 = QgsRuleBasedRendererV2.Rule(symbol1, label=u"それ以外", filterExp="\"%s\" < %.10f" % (field, value), description='rule1')
        rule.appendChild(rule1)
        rule2 = QgsRuleBasedRendererV2.Rule(symbol2, label=str(rate)+u"パーセント", filterExp="\"%s\" >= %.10f" % (field, value), description='rule2')
        rule.appendChild(rule2)

        renderer = QgsRuleBasedRendererV2(rule)
        layer.setRendererV2(renderer)
        self.iface.mapCanvas().refreshAllLayers()

        self.iface.legendInterface().refreshLayerSymbology(layer)
