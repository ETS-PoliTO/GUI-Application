# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 17:45:23 2018

@author: rooster8s
"""

import sys
import os
import pyqtgraph as pg
import pygame
import pandas
from PyQt4 import QtGui,QtCore,Qt,uic
from DBquery import DbQuery
import time
from pytz import utc, timezone
from datetime import datetime
from time import mktime
from functools import partial
import paho.mqtt.client as mqtt
import yaml


form_class = uic.loadUiType("menu.ui")[0] 

class Window(QtGui.QMainWindow,form_class):
    
    #init of Main Window
    def __init__(self,parent=None):      
        QtGui.QMainWindow.__init__(self, parent)
        self.form_class = uic.loadUiType("menu.ui")[0]
        self.setupUi(self)
        self.setWindowTitle('Pds')
        self.setFixedSize(self.size())     
        
        self.centralwidget.showFullScreen()        
        
        folder = "images/";
        #graphic init
        self.graphic.setBackground("w")
        self.graphic.plotItem.showGrid(y=True)
        self.graphic.plotItem.setTitle("Number of people in the last 5 minutes")
        self.graphic.setLabel("left","Number of people", units="N")
        self.graphic.setLabel("bottom","Minutes", units="m")
            
        #visible
        self.graphic_container.hide()
        self.rooms_container.hide()
        self.mac_container.hide()
        
        #config button icon
        icon_graph  = QtGui.QIcon(folder + 'graph.png')
        icon_room  = QtGui.QIcon(folder + 'room.png')
        icon_mac  = QtGui.QIcon(folder + 'mac.png')
        icon_options  = QtGui.QIcon(folder + 'options.png')
        icon_back = QtGui.QIcon(folder + 'back.png')
        icon_help = QtGui.QIcon(folder + 'help.png')
        self.icon_live = QtGui.QIcon(folder + 'live.png')
        self.icon_live_off = QtGui.QIcon(folder + 'live_off.png')

        
        
        self.ppm = QtGui.QPixmap(folder + "logo.jpeg")
        self.logo_esp.setPixmap( self.ppm.scaled(90, 90, QtCore.Qt.KeepAspectRatio) )
        self.logo_esp.show()
        
        self.setWindowIcon(QtGui.QIcon(folder + 'logo.jpeg'))        
                
                       
        self.viewGraph_butt.setIcon(icon_graph)
        self.viewGraph_butt.setIconSize(QtCore.QSize(50,50))
      
        self.viewRooms_butt.setIcon(icon_room)
        self.viewRooms_butt.setIconSize(QtCore.QSize(50,50))
      
        self.viewMacFrequency_butt.setIcon(icon_mac)
        self.viewMacFrequency_butt.setIconSize(QtCore.QSize(50,50))
           
        self.option_butt.setIcon(icon_options)
        self.option_butt.setIconSize(QtCore.QSize(50,50))
        
        self.back_butt.setIcon(icon_back)
        self.back_butt.setIconSize(QtCore.QSize(15,15))
      
        self.back_butt2.setIcon(icon_back)
        self.back_butt2.setIconSize(QtCore.QSize(15,15))
        
        self.back_butt3.setIcon(icon_back)
        self.back_butt3.setIconSize(QtCore.QSize(15,15))
            
        self.help_butt.setIcon(icon_help)
        self.help_butt.setIconSize(QtCore.QSize(20,20))
        
        
            
        #connection button function
        self.viewMacFrequency_butt.clicked.connect(self.viewMac)
        self.viewGraph_butt.clicked.connect(self.viewGraph)
        self.viewRooms_butt.clicked.connect(self.viewDevices)
        self.viewRooms_butt.clicked.connect(self.viewRoom)
        self.searchMac_butt.clicked.connect(self.searchMac)  
        self.option_butt.clicked.connect(self.configuration)
        
        
        self.back_butt.clicked.connect(self.back)
        self.back_butt2.clicked.connect(self.back)
        self.back_butt3.clicked.connect(self.back)
        self.view.clicked.connect(self.plot)
        self.viewDevices_butt.clicked.connect(self.longViewDevices)
        self.ok_pop_up.clicked.connect(self.hidePopUp)
        self.ok_pop_up_2.clicked.connect(self.hidePopUp)
        self.ok_pop_up_3.clicked.connect(self.hidePopUp)
        self.liveButton.clicked.connect(self.liveQuery)
        
        self.help_butt.clicked.connect(self.playsong)
        self.music = False
        pygame.mixer.music.load("music/tavern.wav")
        
        self.error_label.setStyleSheet("QLabel{color:red;}")
        self.error_label2.setStyleSheet("QLabel{color:red;}")
        self.error_label3.setStyleSheet("QLabel{color:red;}")
        
        self.spinBox.setMinimum(1)
        self.spinBox_2.setMinimum(1)
        self.spinBox_3.setMinimum(1)
        
        #config Frame Widget
        self.live = False
        self.frame = Frame(self.frame)
        self.frame.setWindow(self)
        self.frame.setSpinBox(self.spinBox)
        self.frame.resize(740,422)  
        
        self.pop_up.hide()
        self.pop_up_2.hide()
        self.pop_up_3.hide()
        self.calculating.hide()
        
        
        
        self.timestamp_painted = 30

         #config mac query about position
        self.mac = None;
        self.x = []
        self.y = []
        self.t_end = 0
        
        self.mac_pos = []
        for i in range(0,10):
            if i is 0:
                self.mac_pos.append(self.mac1)             
            if i is 1:
                self.mac_pos.append(self.mac2)
            if i is 2:
                self.mac_pos.append(self.mac3)
            if i is 3:
                self.mac_pos.append(self.mac4)
            if i is 4:
                self.mac_pos.append(self.mac5)
            if i is 5:
                self.mac_pos.append(self.mac6)
            if i is 6:
                self.mac_pos.append(self.mac7)
            if i is 7:
                self.mac_pos.append(self.mac8)
            if i is 8:
                self.mac_pos.append(self.mac9)
            if i is 9:
                self.mac_pos.append(self.mac10)
                
            self.mac_pos[i].clicked.connect(partial(self.infoAbout,i))  
     
    
    def hidePopUp(self):
        self.pop_up.hide()
        self.pop_up_2.hide()
        self.pop_up_3.hide()
    
    def viewDevices(self):
        
        self.animation = False
        self.text_devices.setText("Last minute Devices")
        self.liveQuery()
                
        #self.timer.start(60000)
        
        self.scrollBar.setMinimum(1)
        self.scrollBar.setMaximum(1)
    
    def liveQuery(self):
        
        self.liveButton.setIcon(self.icon_live)
        self.liveButton.setIconSize(QtCore.QSize(30,30))
        self.scrollBar.setMinimum(1)
        self.scrollBar.setMaximum(1)
        self.animation = False
        self.live_text.setText("LIVE")
        self.error_label3.setText("")
        self.error_label.setText("")
        print("DOING QUERY..")
        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.liveQuery)
        self.timer.start(60000)
        try:
            with DbQuery() as dh:
                [self.mac,self.x,self.y] = dh.last_minute(1,time.time()) 
                self.live = True
                self.animation = False
                
                #print(self.mac,self.x,self.y)                               
        except Exception as e:
            print(e)    
    
    
    def configuration(self):
        os.system("gedit configurations.yaml");
        #self.refreshBroker()
        
    def longViewDevices(self):

        self.liveButton.setIcon(self.icon_live_off)
        self.liveButton.setIconSize(QtCore.QSize(30,30))        
        
        self.live = False       
        self.mac = None
        self.text_devices.hide()
        self.timer.stop()
        self.live_text.setText("OFF")
        #self.calculating.show()
        try:
            with DbQuery() as dh:
                self.t_start = self.dateToTimestamp(self.dateTime5.dateTime().toPyDateTime()) - self.timestamp_painted
                self.t_end = self.dateToTimestamp(self.dateTime6.dateTime().toPyDateTime()) - self.timestamp_painted
                #t_end = 6120
                
                #Timestamp Control for wrong data
                if self.t_start > self.t_end:
                    self.error_label.setText("Select right data!")
                    return
                else:
                    self.error_label.setText("")
                    
                if self.t_end - self.t_start > 30*60:
                    self.error_label3.setText("Select right data!")
                    return
                else:
                    self.error_label.setText("")

                self.longMacs = dh.movement(self.t_start, self.t_end, 1)
                #self.calculating.hide()
                self.scrollBar.setMinimum(1)
                self.scrollBar.setMaximum(len(self.longMacs))
                if len(self.longMacs) == 0:
                    self.pop_up_2.show()
                else:
                    self.animation = True  
                    self.live = False
        except Exception as e:
            print(e)
            print("There is some error!")
    
    def paintEvent(self,event=None):
        self.frame.update()
            
    def plot(self):
        try:
            self.graphic.plot([1,2,3,4,5],[0,0,0,0,0],clear = "clear")
            with DbQuery() as dh:
                timestamp = self.dateToTimestamp(self.dateTime.dateTime().toPyDateTime()) - self.timestamp_painted
                print(timestamp)
                vet = dh.n_devices(timestamp, 5,1) 
                
                self.graphic.plotItem.plot([1,2,3,4,5],vet, pen='b')               

        except Exception as e:
            print(e)
            print("Unable to connect to database")
            self.pop_up_3.show()
    
    
    def viewGraph(self):       
        self.graphic_container.show()
        self.menu.hide()
        self.graphic.plot([1,2,3,4,5],[0,0,0,0,0],clear = "clear")
    
    def viewRoom(self):      
        self.rooms_container.show()
        self.menu.hide()
        self.live = True
        
    def viewMac(self):
        self.mac_container.show()
        self.menu.hide()
    
    def viewOptions(self):
        self.menu.hide()        
        
    def back(self):
        self.graphic_container.hide()
        self.rooms_container.hide()
        self.mac_container.hide()
        self.menu.show()
        self.refresh()
        self.hidePopUp()
        if self.live:
            self.live = False
            self.timer = None
        self.animation = False
        self.frame.setMacFind(False)
        
    
    def playsong(self):    
        if not self.music:
            pygame.mixer.music.play()
            self.music = True
        else:
            pygame.mixer.music.stop()
            self.music = False
        
    
    def paintEvent(self,event=None): 
        self.frame.update()
        
    
    def timestampToDate(self,timestamp):
        return datetime.fromtimestamp(timestamp)
    
    def dateToTimestamp(self,data):
        return mktime(data.timetuple())
    
    def searchMac(self):
        try:
            with DbQuery() as dh:
                #dh.last_minute(1)
                #dh.n_devices(1528042261, 5)
                timestamp_start = 6000
                timestamp_end = 6120
                
                
                self.t_start = self.dateToTimestamp(self.dateTime3.dateTime().toPyDateTime())
                self.t_end = self.dateToTimestamp(self.dateTime4.dateTime().toPyDateTime())
                
                #Timestamp Control for wrong data
                if self.t_start > self.t_end:
                    print("Errore")
                    self.error_label2.setText("Select right data!")
                    return
                else:
                    self.error_label.setText("")
                [self.intervals,self.mac,self.freq] = dh.long_period_stat(self.t_start,self.t_end,1,10)
                
                if len(self.mac) == 0:
                    self.pop_up.show()
                
                for i in range(0,len(self.mac)):
                   self.mac_pos[i].setText("#"+str(i+1)+"  "+self.mac[i])    
                #print(datetime.fromtimestamp(self.intervals[self.mac[0]][0]))                         

        except Exception as e:
            print(e)
            print("Unable to connect to database")   
            self.pop_up.show()
        
    def getDevicesPosition(self):
        return self.mac,self.x,self.y
    
    def getLongDevicesPosition(self):
        return self.longMacs
    
    def infoAbout(self,pos):
        if self.mac is not None:
            
            day = False
            
            self.macText.clear()
            self.macText.setTextColor(QtGui.QColor(0,0,110))
            self.macText.append("Mac Address: "+self.mac[pos])

            if abs(self.t_end-self.t_start)<60*60:
                string = "over 2 minutes"
            elif abs(self.t_end-self.t_start)<60*60*24:
                string = "over 30 minuts"
            elif abs(self.t_end-self.t_start)<60*60*24*7:
                string = "over 2 hours"
                day = True
            else:
                string = "over 1 day"
                day = True
               
            self.macText.append("  Frequency: "+str(self.freq[pos])+" time(s) ("+string+")")
            self.macText.append("")
            self.macText.append(" -Intervals-")
            for i in range(0,len(self.intervals[self.mac[pos]])):
                data = datetime.fromtimestamp(self.intervals[self.mac[pos]][i])
                data2 = data.time()
                if day:
                    self.macText.append("On "+data.strftime("%d %B %Y"))
                else:
                    self.macText.append("from "+str(data2.hour)+" to "+str(data2.hour+1)+" on "+data.strftime("%d %B %Y"))
        self.macText.append("")
    
    def getLive(self):
        return self.live
    
    def getAnimation(self):
        return self.animation
    
    def getScrollBar(self):
        return self.scrollBar
    
    def getTimestampStart(self):
        return self.t_end

    def refresh(self):
        self.macText.clear()
        self.intervals = None
        self.macs = None
        self.error_label2.setText("")
        for i in range(0,10):
            self.mac_pos[i].setText("#"+str(i+1))
            
    def refreshBroker(self):
        
        with open("configurations.yaml", 'r') as stream:
            try:
                broker_address="192.168.1.6" 
                client = mqtt.Client("GUI") #create new instance
                client.connect(broker_address) #connect to broker 
                print(yaml.load(stream))
                client.publish("ETS/configuration",print(yaml.load(stream)))
            except:
                print("NONE")   
            
        
class Frame(QtGui.QFrame):
           
    def paintEvent(self,event=None):
        
        folder = "images/";        
        
        height = self.size().height() * 1.0
        width = self.size().width() * 1.0       
        K = height/width
        
        #cerco da file congifurazione le dimensioni della stanza
        room_h = 8
        room_w = 11
        k = room_h/room_w
        
        if K - k > 0:
            room_w_scaled = width - 1
            room_h_scaled = room_h*width/room_w
        else:
            room_h_scaled = height - 1
            room_w_scaled = room_w*height/room_h
        
        self.border_w = (width - room_w_scaled) / 2
        self.border_h = (height - room_h_scaled) / 2
        
        self.border_h = 0
        
        color_w = QtGui.QColor(61, 68, 133)
        color_white = QtGui.QColor(255,255,255)
        
        
        person = QtGui.QPixmap(folder + "person.png")
        person_hidden = QtGui.QPixmap(folder + "person_hidden.png")
        person_resize = person.scaled(20, 20, QtCore.Qt.KeepAspectRatio)
        person_hidden_resize = person_hidden.scaled(20, 20, QtCore.Qt.KeepAspectRatio)
        
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(color_w))   
        
        
        qp.fillRect(0,0,width,height,color_w )
        qp.drawRect(self.border_w,self.border_h,room_w_scaled - 1,room_h_scaled - 1)
        qp.fillRect(self.border_w+1,self.border_h+1,room_w_scaled - 2,room_h_scaled - 2,color_white )
        
        self.coff_x = (room_w_scaled-20)/(room_w)     
        self.coff_y = (height-21)/(room_h)
        
        
        #qp.drawPixmap(270,100,room)
        #qp.drawPixmap(self.window.x[0],self.window.y[0],person_resize)
        if self.window.getLive():
            [self.mac,self.x,self.y] = self.window.getDevicesPosition()
            if self.mac is not None:
    
                for i in range(0,len(self.x)):
                    if self.mac[i].find("HiddenMAC") != -1:
                        qp.drawPixmap(self.x[i]*self.coff_x + self.border_w,self.y[i]*self.coff_y,person_hidden_resize)
                    else:
                        qp.drawPixmap(self.x[i]*self.coff_x + self.border_w,self.y[i]*self.coff_y,person_resize)
                if self.mac_find:
                    if self.x[self.index]*self.coff_x + self.border_w + 20 + 20 + 146 > width*5/6:                  
                        off_mirror = 166
                    else:
                        off_mirror = 0
                        
                    qp.fillRect(self.x[self.index]*self.coff_x + self.border_w + 20 - off_mirror,self.y[self.index]*self.coff_y,150,25,color_w)
                    qp.fillRect(self.x[self.index]*self.coff_x + self.border_w + 22 - off_mirror,self.y[self.index]*self.coff_y+2,146,21,color_white)
                    qp.drawText((self.x[self.index]*self.coff_x + self.border_w + 20 - off_mirror)+10,(self.y[self.index]*self.coff_y)+15,self.mac[self.index])
        
        if self.window.getAnimation():
            
            self.longMacs = self.window.getLongDevicesPosition()
            valx = self.window.getScrollBar().value()
            val = self.window.getScrollBar().maximum() - valx
            if val is not self.lastval:
                self.lastval = val
                self.mac_find = False
                
            self.ind = self.window.getTimestampStart() - (val) * 60
            self.macz = self.longMacs[self.ind]
            
            for i in range(0,len(self.macz)):
                if self.macz[i][0].find("HiddenMAC") != -1:
                    qp.drawPixmap(self.macz[i][1]*self.coff_x + self.border_w,self.macz[i][2]*self.coff_y,person_hidden_resize)
                else:
                    qp.drawPixmap(self.macz[i][1]*self.coff_x + self.border_w,self.macz[i][2]*self.coff_y,person_resize)
                    
            if self.mac_find:              
                    if self.macz[self.index][1]*self.coff_x + self.border_w + 20 + 20 + 146 > width*5/6:
                        off_mirror = 166
                    else:
                        off_mirror = 0
                        
                    qp.fillRect(self.macz[self.index][1]*self.coff_x + self.border_w + 20 - off_mirror,self.macz[self.index][2]*self.coff_y,150,25,color_w)
                    qp.fillRect(self.macz[self.index][1]*self.coff_x + self.border_w + 22 - off_mirror,self.macz[self.index][2]*self.coff_y+2,146,21,color_white)
                    qp.drawText((self.macz[self.index][1]*self.coff_x + self.border_w + 20 - off_mirror)+10,(self.macz[self.index][2]*self.coff_y)+15,self.macz[self.index][0])
            
        
    def setSpinBox(self,spinbox):
        self.spinBox = spinbox
    
    def setMacFind(self,value):
            self.mac_find = value
    
    def getHeight(self):
        return self.size().width()
    
    def getWidth(self):
        return self.size().height()
        
    def setWindow(self,window):
        self.window = window
        self.index = None
        self.mac_find = None
        self.lastval = 0
        
    def mousePressEvent(self, QMouseEvent):
        mouse_x = QMouseEvent.pos().x()
        mouse_y = QMouseEvent.pos().y()
        i=0
        
        if self.window.getLive():
            self.mac_find = False
            while i < len(self.x):
                if mouse_x  >= self.x[i]*self.coff_x + self.border_w and mouse_x  <= self.x[i]*self.coff_x + self.border_w+20 and mouse_y  >= self.y[i]*self.coff_y and mouse_y  <= self.y[i]*self.coff_y+20:
                    self.mac_find = True
                    self.index = i                    
                    self.update()
                    return
                i = i+1
                
        if self.window.getAnimation():    
            self.mac_find = False
            while i < len(self.macz):
                if mouse_x  >= self.macz[i][1]*self.coff_x + self.border_w and mouse_x  <= self.macz[i][1]*self.coff_x + self.border_w+20 and mouse_y  >= self.macz[i][2]*self.coff_y and mouse_y  <= self.macz[i][2]*self.coff_y+20:
                    self.mac_find = True
                    self.index = i                    
                    self.update()
                    return
                i = i+1
        #print(mouse_x,mouse_y)
        self.mac_find = False
    
        
        

def main():
    #gui app init
    app = QtGui.QApplication(sys.argv) 
    app.setWindowIcon(QtGui.QIcon('logo.jpeg')) 
    pygame.init()
    
    #window object
    window = Window(None)
    window.show() 
    
    n = app.exec_()
    
    exit(n)
    
if __name__ =='__main__':
    main()