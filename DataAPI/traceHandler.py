
import codecs

TRACE_LEVEL = 1
TRACE_TO_FILE = True
TRACE_LOG_FILE = "traceLog.txt"


class TraceHandler( object ):

    def __init__( self, \
                  trace_level=TRACE_LEVEL, \
                  trace_to_file=TRACE_TO_FILE, \
                  trace_log_file=TRACE_LOG_FILE ):

        self._message = u""
        self._err_message = u""

        self._trace_buffer = u""

        self._trace_level = trace_level
        self._trace_to_file = trace_to_file
        self._trace_log_file = trace_log_file

        if self._trace_to_file:
            # self._traceLogStream = open( self._trace_log_file, "wb" )
            self._traceLogStream = codecs.open( self._trace_log_file, "wb", "utf-8" )
            # self._traceLogStream = None
        else:
            self._traceLogStream = None

        self.trace( "TraceHandler.__init__", 6 )


    def _convertToUnicode( self, msg ):

        if isinstance( msg, str ):
            u_msg = msg.decode("utf-8")
        else:
            u_msg = msg

        u_msg += u"\n"

        return u_msg


    def clearMessage( self ):
        self._message = u""


    def addMessage( self, msg ):
        u_msg = self._convertToUnicode( msg )
        self._message += u_msg


    def setMessage( self, msg ):
        u_msg = self._convertToUnicode( msg )
        self._message = u_msg


    def getMessage( self ):
        return self._message


    def clearErrMessage( self ):
        self._err_message = u""


    def addErrMessage( self, msg ):
        u_msg = self._convertToUnicode( msg )
        self._err_message += u_msg


    def setErrMessage( self, msg ):
        u_msg = self._convertToUnicode( msg )
        self._err_message = u_msg


    def getErrMessage( self ):
        return self._err_message


    def getStatus( self ):
        if u"" == self._err_message:
            return True
        else:
            return False


    def clearTrace( self ):
        self._trace_buffer = u""

    
    def trace( self, msg, lvl ):

        if lvl <= self._trace_level:

            u_msg = self._convertToUnicode( msg )

            # Record trace data to be shown to the user.
            self._trace_buffer += u_msg

            if None != self._traceLogStream:
                # self._traceLogStream.write( u_msg.encode("utf-8") )
                self._traceLogStream.write( u_msg )


    def getTrace( self ):
        return self._trace_buffer


    def finalize( self ):

        self.trace( "TraceHandler.finalize", 6 )

        if None != self._traceLogStream:

            self._traceLogStream.flush()
            self._traceLogStream.close()

        else:

            if self._trace_to_file:

                # self._traceLogStream = open( self._trace_log_file, "wb" )
                self._traceLogStream = codecs.open( self._trace_log_file, "wb", "utf-8" )

                # self._traceLogStream.write( self._trace_buffer.encode("utf-8") )
                self._traceLogStream.write( self._trace_buffer )

                self._traceLogStream.flush()
                self._traceLogStream.close()
