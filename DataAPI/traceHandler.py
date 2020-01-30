

TRACE_LEVEL = 1
TRACE_TO_FILE = True
TRACE_LOG_FILE = "traceLog.txt"


class TraceHandler( object ):

    def __init__( self, \
                  error_msg=None, trace_buffer=None, \
                  message=None, err_message=None, \
                  trace_level=TRACE_LEVEL, \
                  trace_to_file=TRACE_TO_FILE, \
                  trace_log_file=TRACE_LOG_FILE ):

        # This will correspond to an external source.
        if None != error_msg:
            self._error_msg = error_msg
        else:
            self._error_msg = ""

        # This might get referenced externally.
        if None != trace_buffer:
            self._trace_buffer = trace_buffer
        else:
            self._trace_buffer = ""

        if None != message:
            self._message = message
        else:
            self._message = ""

        if None != err_message:
            self._err_message = err_message
        else:
            self._err_message = ""

        self._trace_level = trace_level

        if trace_to_file:
            self.traceLogStream = open( trace_log_file, "wb" )
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

        if lvl <= self._trace_level:

            record = msg + "\n"

            # Record trace data to be shown to the user.
            self._trace_buffer += record

            if None != self.traceLogStream:
                self.traceLogStream.write( record )


    def set_error_trace( self, msg ):
        self.trace( msg, 1 )
        self.set_error( msg )


    def set_error( self, msg ):
        self._error_msg = msg


    def read_trace_log( self ):
        # Return the trace data.
        return_trace = self._trace_buffer
        self._trace_buffer = ""
        return (True, return_trace)
