


class ADSClassicInputStream(object):

    def __init__(self, file_):
        self._file = file_
        self._iostream = open(file_, 'r')
        

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()
    
    def __iter__(self):
        return self
    
    def next(self):
        print 'next'
        return self._iostream.next()
    
    @classmethod
    def open(cls, file_):
        return cls(file_)

    def close(self):
        self._iostream.close()
        del self._iostream


    def read(self, size=-1):
        #print 'read'
        #return self._iostream.read(size)
        return self._iostream.readline()
    

    def readline(self):
        print 'readline'
        return self._iostream.readline()
    
    