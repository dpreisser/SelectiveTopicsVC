

TRACE_LEVEL = 1
TRACE_TO_FILE = True
TRACE_LOG_FILE = "traceLog.txt"


class TraceHandler( object ):

    def __init__( self ):

        self.trace_buffer = ""

        self._message = ""
        self._err_message = ""

        self.trace_level = TRACE_LEVEL

        if TRACE_TO_FILE:
            self.traceLogStream = open( TRACE_LOG_FILE, "wb" )
        else:
            self.traceLogStream = None


    def clearMessage( self ):
        self._message = ""


    def addMessage( self, msg ):
        self._message += msg
        self._message += "\n"


    def setMessage( self, msg ):
        self._message = msg
        self._message += "\n"


    def getMessage( self ):
        return self._message


    def clearErrMessage( self ):
        self._err_message = ""


    def addErrMessage( self, msg ):
        self._err_message += msg
        self._err_message += "\n"


    def setErrMessage( self, msg ):
        self._err_message = msg
        self._err_message += "\n"


    def getErrMessage( self ):
        return self._err_message


    def getStatus( self ):
        if "" == self._err_message:
            return True
        else:
            return False


    def trace( self, msg, lvl ):

        if lvl <= self.trace_level:

            record = msg + "\n"

            # Record trace data to be shown to the user.
            self.trace_buffer += record

            if None != self.traceLogStream:
                self.traceLogStream.write( record )


    def set_error_trace( self, msg ):
        self._trace( msg, 1 )
        # self._set_error( msg )


    def read_trace_log( self ):
        # Return the trace data.
        return_trace = self.trace_buffer
        self.trace_buffer = ""
        return (True, return_trace)
