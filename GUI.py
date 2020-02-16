from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from functools import partial
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import gc
from mpl_toolkits.axes_grid1 import make_axes_locatable


import lib.CircleImage
import lib.Particle

import json
import os.path

class MainWindow(QWidget):
    def __init__(self, path='C:\\Users\Stefan\\bwSyncAndShare\\LehrlaborEnergietechnik (Matthias Probst)\\imgs\\LaserDuenn_Vol250_pd200\\Cam1_001A\\000005.tiff'):#'.\\pictures\\Cam1_0001A.b16'):
        super().__init__()
        self.useCanney = False
        self.Picturepath = path
        self.UseHigpass = False
        self.UseHough = False
        self.initUI()

    def initUI(self):
        self.label = None
        self.overallLayout = QHBoxLayout()
        toolbarLayout = QVBoxLayout()
        self.overallLayout.addLayout(toolbarLayout)
        # settings = QHBoxLayout()

        applyButton = QPushButton('apply Settings')
        applyButton.clicked.connect(self.applyButtonClicked)
        self.dont_use_default_order = QCheckBox('don\'t use default order')
        toolbarLayout.addWidget(self.dont_use_default_order)

        sublay = QHBoxLayout()
        selectButton = QPushButton('Select Folder and Export Name', self)
        selectButton.setToolTip('open dialog to select folder')
        selectButton.clicked.connect(self.on_click_select_button)
        # bar in which filepath is displayed and can be modified
        qle = QLineEdit(self)
        qle.displayText()
        qle.setText(self.Picturepath)
        qle.textChanged[str].connect(self.onChanged)
        sublay.addWidget(qle)
        sublay.addWidget(selectButton)
        toolbarLayout.addLayout(sublay)
        self.overallLayout.addLayout(toolbarLayout)
        self.setLayout(self.overallLayout)
        saveButton = QPushButton('save Filtersettings')
        saveButton.clicked.connect(self.save_settings)

        self.cropping = OneFilter('crop picture', {'xCrop1': 0, 'xCrop2': 255, 'ycrop1': 0, 'ycrop2': 255},
                                  self)  # , self.wrapper_widget)
        self.filtersettings = Settings(self)
        toolbarLayout.addWidget(self.filtersettings)
        toolbarLayout.addWidget(self.cropping)
        toolbarLayout.addWidget(applyButton)
        toolbarLayout.addWidget(saveButton)
        # fin_butt_layout = QHBoxLayout()
        # settings.addLayout(fin_butt_layout)
        # toolbarLayout.addLayout(settings)
        #self.setLayout(toolbarLayout)
        # self.setLayout(self.overallLayout)
        #self.setFixedSize(500,1000)
        self.show()

    def onChanged(self, text):
        self.Picturepath = os.path.normpath(text.encode('raw_unicode_escape').decode())

    def on_click_select_button(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.pco)", options=options)
        if fileName:
            self.Picturepath = fileName
            self.qle.setText(self.Picturepath)

    def applyButtonClicked(self):
        settings = {}
        for obj in gc.get_objects():
            if isinstance(obj, OneFilter):
                settings.update(obj.filtervalue)
        '''
        settings.update(self.cropping.filtervalue)
        settings.update(self.filtersettings.canney.filtervalue)
        settings.update(self.filtersettings.HighPass.filtervalue)
        settings.update(self.filtersettings.HoughFilter.filtervalue)
        '''
        for key in settings.keys():
            if len(str(settings[key]).split('.'))==2:
                settings[key] = float(settings[key])
            else:
                settings[key] = int(settings[key])
        self.refresh_and_apply_parameters(settings)

    def refresh_and_apply_parameters(self, settings):
        #try:

        picture = lib.CircleImage.CircleImage(os.path.abspath(self.Picturepath), settings)
        pic=picture.img
        print('picture loading worked')
        fig, axs = plt.subplots(1,1)
        img1 = axs.imshow(pic)
        if self.cropping.activateFilterCheckbox.isChecked():
            picture.cropPicture(int(settings['xCrop1']), int(settings['xCrop2']) ,int(settings['ycrop1']), int(settings['ycrop2']))
            pic = picture.img
        filters_to_apply = {}
        for key in self.filtersettings.filters.keys():                          #write filters which should be activated to new dict
            if self.filtersettings.filters[key].activateFilterCheckbox.isChecked():
                filters_to_apply.update({key : self.filtersettings.filters[key]})

        #now sort the list to apply filters in right order
        sortingList = {}

        if self.dont_use_default_order.isChecked():
            for key in filters_to_apply:
                if type(filters_to_apply[key].whenToUse) is list:
                    for num in filters_to_apply[key].whenToUse:
                        sortingList.update({num: {key :filters_to_apply}})
                if type(filters_to_apply[key].whenToUse) is int:
                    sortingList.update({filters_to_apply[key].whenToUse: {key: filters_to_apply}})
            right_order = list(sortingList.keys())
            right_order.sort()


            for key in right_order:
                filter = sortingList[key]
                key = list(filter.keys())[0]
                if key == 'detect_circles':# and filter[key].activateFilterCheckbox.isChecked():
                    picture.detect_circles(image=pic)
                    fig, axs = plt.subplots(1, 1)
                    img1=axs.imshow(pic)
                    try:
                        for circle in picture.circles[0, :]:
                            circ = plt.Circle((circle[0], circle[1]), circle[2], fill=False, color='g')
                            axs.add_artist(circ)
                    except TypeError:
                        print('circle detection didnt work, please try with different parameter')
                    plt.savefig('pictoshow.png')
                elif key =='get_enclosing_circles':
                    picture.get_enclosing_circle(image=pic)
                    fig, axs = plt.subplots(1, 1)
                    img1=axs.imshow(pic)
                    try:
                        circ = plt.Circle(circle[0], circle[1], fill=False, color='r')
                        axs.add_artist(circ)
                    except TypeError:
                        print('circle detection didnt work, please try with different parameter')
                    plt.savefig('pictoshow.png')
                    print(circle)
                else:
                    pic = getattr(picture, key)()
                    fig, axs = plt.subplots(1, 1)
                    img1 = axs.imshow(pic)
        else:
            for key in filters_to_apply:
                if key == 'detect_circles':  # and filter[key].activateFilterCheckbox.isChecked():
                    picture.detect_circles(image=pic)
                    fig, axs = plt.subplots(1, 1)
                    img1 = axs.imshow(pic)
                    try:
                        for circle in picture.circles[0, :]:
                            circ = plt.Circle((circle[0], circle[1]), circle[2], fill=False, color='r')
                            axs.add_artist(circ)
                    except TypeError:
                        print('circle detection didnt work, please try with different parameter')
                    plt.savefig('pictoshow.png')
                elif key == 'get_enclosing_circles':
                    picture.get_enclosing_circle(image=pic)
                    fig, axs = plt.subplots(1, 1)
                    img1=axs.imshow(pic)
                    try:
                        circ = plt.Circle(circle[0], circle[1], fill=False, color='r')
                        axs.add_artist(circ)
                    except TypeError:
                        print('circle detection didnt work, please try with different parameter')
                    plt.savefig('pictoshow.png')
                    print(circle)
                else:
                    pic = getattr(picture, key)()
                    fig, axs = plt.subplots(1, 1)
                    img1 = axs.imshow(pic)


        cbar3 = fig.colorbar(img1)
        plt.savefig('pictoshow.png')
        plt.close('all')

        pix = QPixmap('pictoshow.png')
        print('converting to pixmap worked')
        if self.label is None:
            self.label = QLabel()
            self.overallLayout.addWidget(self.label)
        else:
            self.label.setPixmap(pix)
        print('settinng pixmap worked')
        print('adding pixmap to layout worked')
        #self.show()
        self.overallLayout.update()
        print('updating layout worked')
        #return pic
        #except (FileNotFoundError ,TypeError):
        #    error_dialog = QErrorMessage()
        #    error_dialog.showMessage('invalid filepath')
        #    print('invalid filepath')


    def save_settings(self, settings):
        pass
        """
        SettingsToSave = {}

        filters_to_apply = {}
        for key in self.filtersettings.filters.keys():  # write filters which should be activated to new dict
            if self.filtersettings.filters[key].activateFilterCheckbox.isChecked():
                filters_to_apply.update({key: self.filtersettings.filters[key]})

        # now sort the list to apply filters in right order
        sortingList = {}

        if self.dont_use_default_order.isChecked():
            for key in filters_to_apply:
                if type(filters_to_apply[key].whenToUse) is list:
                    for num in filters_to_apply[key].whenToUse:
                        sortingList.update({num: {key: filters_to_apply}})
                if type(filters_to_apply[key].whenToUse) is int:
                    sortingList.update({filters_to_apply[key].whenToUse: {key: filters_to_apply}})
            right_order = list(sortingList.keys())
            right_order.sort()
            with open('data.json', 'w') as fp:
                json.dump([right_order.keys(), settings], fp)
        else:
            with open('data.json', 'w') as fp:
                json.dump([right_order.keys(), settings], fp)

        '''
        SettingsToSave.update(self.canney.filtervalue)
        SettingsToSave.update(self.HighPass.filtervalue)
        SettingsToSave.update(self.canney.filtervalue)
        '''
        for key in filters_to_apply
        with open('data.json', 'w') as fp:
            json.dump(self.filtersettings.filters.keys(), fp)
        """


class Settings(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        #self.tab1 = QWidget()
        #self.tab2 = QWidget()
        self.filters = {}   #list to save all OneFilter objects in for easier acces through looping

        self.tab2 = QScrollArea()
        self.tab2.setWidget(QWidget())
        #tab1_layout = QVBoxLayout(self.tab2.widget())
        self.tab2.setWidgetResizable(True)

        self.tab3 = QWidget()
        self.tab4 = QWidget()



        #self.addTab(self.tab1, "finish")
        self.addTab(self.tab2, "highpass")
        self.addTab(self.tab3, "blurring")
        self.addTab(self.tab4, 'circle detection')
        #self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        self.tab4UI()




        #self.init_ui()
    def tab1UI(self):
        pass

    def tab2UI(self):
        scrollLayout = QVBoxLayout()
        self.sobel = OneFilter('Use Sobel', {'xdim':3, 'ydim':3}, self.tab2)#, self.wrapper_widget)
        self.filters.update({'sobel' : self.sobel})
        scrollLayout.addWidget(self.sobel)

        self.laplace = OneFilter('Laplace', {'laplace ksize': 9}, self.tab2)#, self.wrapper_widget)
        scrollLayout.addWidget(self.laplace)
        self.filters.update({'laplace' : self.laplace})

        self.backgroundFilter = OneFilter('subtract_bg', {})
        self.filters.update({'subtract_bg' : self.backgroundFilter})
        scrollLayout.addWidget(self.backgroundFilter)

        self.localBackground = OneFilter('subtract_local_bg', {'d': 10})
        self.filters.update({'subtract_local_bg': self.localBackground})
        scrollLayout.addWidget(self.localBackground)


        self.canney = OneFilter('canny',
                                {'lower_th_canny': 10, 'upper_th_canny': 250, 'CA_filtersize': 9, 'CA_sigmaColor': 10,
                                 'CA_sigmaSpace': 10},self.tab2)#, self.wrapper_widget)
        scrollLayout.addWidget(self.canney)
        self.filters.update({'canny':self.canney})

        self.tab2.widget().setLayout(scrollLayout)

        self.HighPass = OneFilter('HighPass', {'highpass ksize':9},self.tab2)#, self.wrapper_widget)
        scrollLayout.addWidget(self.HighPass)
        self.filters.update({'high_pass' : self.HighPass})

        self.erode = OneFilter('erode', {}, self.tab2)
        scrollLayout.addWidget(self.erode)
        self.filters.update({'erode': self.erode})

        self.open = OneFilter('open', {}, self.tab2)
        scrollLayout.addWidget(self.open)
        self.filters.update({'open': self.open})

        self.mean_thresholding = OneFilter('adaptive_threshold_mean', {'thres_mean_a':5, 'thres_mean_b':255})
        scrollLayout.addWidget(self.mean_thresholding)
        self.filters.update({'adaptive_threshold_mean': self.mean_thresholding})


    def tab3UI(self):
        scrollLayout=QVBoxLayout()
        self.Median = OneFilter('Use Median', {'median ksize':9},self.tab2)#, self.wrapper_widget)
        self.filters.update({'medfilt': self.Median})
        scrollLayout.addWidget(self.Median)

        self.adaptive_threshold_gauss = OneFilter('Usse adaptive gauss', {'a':11, 'b':12})
        self.filters.update({'adaptive_threshold_gauss': self.adaptive_threshold_gauss})
        scrollLayout.addWidget(self.adaptive_threshold_gauss)

        self.adaptive_threshold_mean = OneFilter('Usse adaptive mean', {'a': 11, 'b': 12})
        self.filters.update({'adaptive_threshold_mean': self.adaptive_threshold_mean})
        scrollLayout.addWidget(self.adaptive_threshold_mean)


        self.bilateral = OneFilter('Bilateral', {'bilateral ksize':9, 'sigmaColor':10, 'sigmaSpace':10},self.tab3)#, self.wrapper_widget)
        scrollLayout.addWidget(self.bilateral)
        self.filters.update({'bilateral': self.bilateral})


        self.tab3.setLayout(scrollLayout)

    def tab4UI(self):
        scrollLayout=QVBoxLayout()
        self.HoughFilter = OneFilter('Hough Transformation', {'par1':50, 'par2':5,'dp':0.4, 'minDist':15, 'minRad':5, 'maxRad':20}, self.tab3)#, self.wrapper_widget)
        scrollLayout.addWidget(self.HoughFilter)
        self.tab4.setLayout(scrollLayout)
        self.filters.update({'detect_circles': self.HoughFilter})
        self.EnclosingCircle = OneFilter('get_enclosing_circle',{})
        self.filters.update({'get_enclosing_circle': self.EnclosingCircle})
        scrollLayout.addWidget(self.EnclosingCircle)

#todo methode schreiben um aus dictionaries mit onefiler objekten den filter in CircleImage auszuführen


class OneFilter(QWidget):
    def __init__(self, name, filtervaluenames, parent=None):
        super().__init__(parent=parent)
        if type(filtervaluenames) is list:
            self.filtervalue = [{name:0} for name in filtervaluenames]
            a={}
            [a.update(element) for element in self.filtervalue]
            self.filtervalue = a
        elif type(filtervaluenames) is dict:
            self.filtervalue = filtervaluenames
        self.whenToUse = 0
        self.initUI(name)


    def initUI(self, key):
        layout=QVBoxLayout()
        self.activateFilterCheckbox = QCheckBox(key)
        self.activateFilterCheckbox.stateChanged.connect(self.activateFilterClicked)
        layout.addWidget(self.activateFilterCheckbox)
        self.setLayout(layout)
        whenToUse = QLineEdit(str(self.whenToUse))
        #validator = QIntValidator(0, 10)
        #whenToUse.setValidator(validator)
        whenToUse.textChanged.connect(self.numChanged)
        layout.addWidget(whenToUse)
        for key in self.filtervalue.keys():
            sublayout=QHBoxLayout()
            sublayout.addWidget(QLabel(key))
            qle = QLineEdit(str(self.filtervalue[key]))
            qle.textChanged.connect(partial(self.textchanged, key))
            sublayout.addWidget(qle)
            layout.addLayout(sublayout)
        self.setFixedSize(self.sizeHint())
        self.show()

    def numChanged(self, text):
        #if len(text.split(','))>0
        try:
            self.whenToUse = int(text)
        except ValueError:
            try:
                self.whenToUse=[int(i) for i in text.split(',')]
            except ValueError:
                print('invalid value in whentouse field')


    def textchanged(self, name, text):
        self.filtervalue[name] = text
        print(self.filtervalue)

    def activateFilterClicked(self):
        self.filterActivated = self.activateFilterCheckbox.isChecked()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())