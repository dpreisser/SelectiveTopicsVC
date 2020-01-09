
from datetime import timedelta, datetime, tzinfo

class GMT1(tzinfo):

    def utcoffset(self, dt):
        return timedelta(hours=1) + self.dst(dt)
    
    def dst(self, dt):
        # DST starts last Sunday in March
        d = datetime(dt.year, 4, 1)   # ends last Sunday in October
        self.dston = d - timedelta(days=d.weekday() + 1)
        d = datetime(dt.year, 11, 1)
        self.dstoff = d - timedelta(days=d.weekday() + 1)
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return timedelta(hours=1)
        else:
            return timedelta(0)
        
    def tzname(self,dt):
        return "GMT +1"


class GMT2(tzinfo):

    def utcoffset(self, dt):
        return timedelta(hours=2) + self.dst(dt)

    def dst(self, dt):
        d = datetime(dt.year, 4, 1)
        self.dston = d - timedelta(days=d.weekday() + 1)
        d = datetime(dt.year, 11, 1)
        self.dstoff = d - timedelta(days=d.weekday() + 1)
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return timedelta(hours=1)
        else:
            return timedelta(0)

    def tzname(self,dt):
        return "GMT +2"


if "__main__" == __name__:

    gmt1 = GMT1()

    # Daylight Saving Time
    dt1 = datetime(2006, 11, 21, 16, 30, tzinfo=gmt1)
    print( dt1 )
    print( dt1.dst() )
    print( dt1.utcoffset() )

    dt2 = datetime(2006, 6, 14, 13, 0, tzinfo=gmt1)
    print( dt2 )
    print( dt2.dst() )
    print( dt2.utcoffset() )

    # Convert datetime to another time zone
    dt3 = dt2.astimezone(GMT2())
    print( dt3 )

    utc_tpl2 = dt2.utctimetuple()
    utc_dt2 = datetime( utc_tpl2.tm_year, utc_tpl2.tm_mon, utc_tpl2.tm_mday, \
                        utc_tpl2.tm_hour, utc_tpl2.tm_min, utc_tpl2.tm_sec )  
    print( utc_tpl2 )
    print( utc_dt2.isoformat( "T" ) )
    
    utc_tpl3 = dt3.utctimetuple()
    utc_dt3 = datetime( utc_tpl3.tm_year, utc_tpl3.tm_mon, utc_tpl3.tm_mday, \
                        utc_tpl3.tm_hour, utc_tpl3.tm_min, utc_tpl3.tm_sec )  
    print( utc_tpl3 )
    print( utc_dt3.isoformat( "T" ) )

    print( dt2.replace(tzinfo=None) )
    print( dt3.replace(tzinfo=None) )

    print( dt2.isoformat( "T" ) ) 
    print( dt2.strftime( "%d-%b-%Y %H:%M:%S" ) ) 
    print( dt2.strftime( "%d-%b-%Y %H:%M:%S %Z" ) )
    print( dt2.strftime( "%d-%b-%Y %H:%M:%S%z" ) ) 

    utc_dts = datetime( 1900, 1, 1, 0, 0, 0 ) + dt2.utcoffset()
    print( dt2.strftime( "%d-%b-%Y %H:%M:%S" ) + utc_dts.strftime( "+%H:%M" ) )
