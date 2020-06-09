
import sys

from PySide import QtGui
from PySide import QtCore


from datetime import datetime
import time


TIME_SLEEP = 5


class AsyncPrint( QtCore.QObject ):

    addMessageSignal = QtCore.Signal(str)

    def __init__( self, myWidget, parent=None ):

        super( AsyncPrint, self ).__init__( parent )

        self.myWidget = myWidget


    def asyncPrint( self ):
        dts = datetime.now() 
        # self.myWidget.addMessage( "Entering asyncPrint: %s" % str(dts) )
        self.addMessageSignal.emit( "Entering asyncPrint: %s" % str(dts) )
        time.sleep( TIME_SLEEP )
        dts = datetime.now()
        # self.myWidget.addMessage( "Leaving asyncPrint: %s" % str(dts) )
        self.addMessageSignal.emit( "Leaving asyncPrint: %s" % str(dts) )


class MyWidget( QtGui.QWidget ):

    def __init__( self, parent=None ):

        super( MyWidget, self ).__init__( parent )

        # self.aboutToQuit.connect( self.quitAsyncPrintThread )
        self.asyncPrint = AsyncPrint( None )
        self.asyncPrint.addMessageSignal.connect( self.addMessage )

        # Buttons
        l_hbxButtons = QtGui.QHBoxLayout()
        l_hbxButtons.setDirection( QtGui.QBoxLayout.RightToLeft )

        l_butClear = QtGui.QPushButton( "Clear" )
        l_butClear.clicked.connect( self.clear_clicked )
        l_hbxButtons.addWidget( l_butClear )

        l_butAsync = QtGui.QPushButton( "Async" )
        # l_butAsync.clicked.connect( self.async_clicked )
        l_butAsync.clicked.connect( self.asyncPrint.asyncPrint )
        l_hbxButtons.addWidget( l_butAsync )

        self.butSync = QtGui.QPushButton( "Sync" )
        self.butSync.clicked.connect( self.sync_clicked )
        l_hbxButtons.addWidget( self.butSync )

        l_hbxButtons.addStretch( 1 )

        # Message
        l_hbx_msg = QtGui.QHBoxLayout()
    
        self.pte_msg = QtGui.QPlainTextEdit()
        self.pte_msg.setReadOnly( True )
        # policy = self.pte_msg.sizePolicy()
        # policy.setVerticalStretch( 1 )
        # self.pte_msg.setSizePolicy( policy )
        # self.pte_msg.setMinimumHeight( 100 )
        # self.pte_msg.setMaximumHeight( 500 )
        # self.pte_msg.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )
        l_hbx_msg.addWidget( self.pte_msg )

        l_grp_msg = QtGui.QGroupBox( "Message" )
        l_grp_msg.setLayout( l_hbx_msg )

        l_vbxTab1 = QtGui.QVBoxLayout()
        l_vbxTab1.addLayout( l_hbxButtons )
        l_vbxTab1.addWidget( l_grp_msg )

        self.setLayout( l_vbxTab1 )

        self.createAsyncPrintThread()


    def clearMessage( self ):
        self.pte_msg.clear()

    def addMessage( self, message ):
        self.pte_msg.appendPlainText( message )

    def setMessage( self, message=None ):
        self.pte_msg.setPlainText( message )


    def createAsyncPrintThread( self ):
        self.asyncPrintThread = QtCore.QThread()
        self.asyncPrint.moveToThread( self.asyncPrintThread )
        self.asyncPrintThread.start()


    def quitAsyncPrintThread( self ):

        if self.asyncPrintThread.isRunning():
            print( "Running..." )
            self.asyncPrintThread.quit()
            print( "Before wait..." )
            self.asyncPrintThread.wait()
            print( "After wait..." )
            self.asyncPrintThread.deleteLater()
        else:
            print( "Not running..." )

        print( self.asyncPrintThread.isRunning() )
        print( self.asyncPrintThread.isFinished() )


    def sync_clicked( self ):
        dts = datetime.now() 
        self.addMessage( "Entering sync_clicked: %s" % str(dts) )
        time.sleep( TIME_SLEEP )
        dts = datetime.now()
        self.addMessage( "Leaving sync_clicked: %s" % str(dts) )


    def async_clicked( self ):
        self.asyncPrint.asyncPrint()


    def clear_clicked( self ):
        self.clearMessage()


    def closeEvent( self, event ):
        print( "closeEvent" )
        self.quitAsyncPrintThread()
        event.accept() # let the window close



if "__main__" == __name__:

    app = QtGui.QApplication(sys.argv)
    myWidget = MyWidget()
    myWidget.show()
    sys.exit( app.exec_() )
