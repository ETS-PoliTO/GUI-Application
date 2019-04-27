# ETS Graphic User Interface

This python script is developed for interface the user to the database system to ensure the graphic view of all information about the devices in the room.  
The Application is divided in 4 areas:

- View Graph
- View Room
- View Mac Frequency
- Configuration

![screenshot from 2018-10-31 16-00-17](https://user-images.githubusercontent.com/33552039/47797180-1e33b100-dd26-11e8-9c0f-baa23af09a89.png)


## View Graph

In this section is possible have a graphic plot about the number of devices in a selected room in the last 5 minutes from the time start setted.    
It's possible in this way have control about the influx of people.

![screenshot from 2018-10-31 15-05-49](https://user-images.githubusercontent.com/33552039/47793414-7e265980-dd1e-11e8-8bcd-3a1e3cd0859e.png)

## View Room

A simple view of a room in which is possible select a device and see its mac address.  
It's also possible select a longer time lapse to see an animation about the movement of all devices.

![screenshot from 2018-10-31 16-20-24](https://user-images.githubusercontent.com/33552039/47798550-e67a3880-dd28-11e8-8f46-39d978a3e4a0.png)


## View Mac Frequency

![screenshot from 2018-10-31 16-13-24](https://user-images.githubusercontent.com/33552039/47798187-21c83780-dd28-11e8-94a6-36765aef4d39.png)

## Configuration
This area opens a text editor for configure the .yaml file with all info about the rooms:  

- Number of rooms
- Number of ESP in a room
- Width and Height of a room

## Dependencies

Python bindings for the Qt cross-platform C++ framework: [PyQt4](https://wiki.python.org/moin/PyQt)  
For GraphicPlot: [PyQtGraph](http://www.pyqtgraph.org/)

