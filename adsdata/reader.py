


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
        return self._iostream.next()
    
    @classmethod
    def open(cls, file_):
        return cls(file_)

    def close(self):
        self._iostream.close()
        del self._iostream


    def read(self, size=-1):
        line = self._iostream.readline()
        if len(line) == 0:
            return ''
        return self.process_line(line)
    

    def readline(self):
        line = self._iostream.readline()
        return self.process_line(line)
    
    def process_line(self, line):
        return line
    
    
   
class BibcodeFileReader(ADSClassicInputStream):
    """add id field to bibcode"""
    
    def __init__(self, file_):
        super(BibcodeFileReader, self).__init__(file_)
        self.counter = 1
        
    def process_line(self, line):
        bibcode = line[:-1]
        row = '{}\t{}\n'.format(bibcode, self.counter)
        self.counter += 1
        return row
    
 
class RefereedFileReader(ADSClassicInputStream):
    def __init__(self, file_):
        super(RefereedFileReader, self).__init__(file_)
        
    def process_line(self, line):
        bibcode = line[:-1]
        row = '{}\t{}\n'.format(bibcode, 'T')
        return row
        
class StandardFileReader(ADSClassicInputStream):
    """each line has all values for a single bibcode"""
    def __init__(self, file_type_, file_):
        super(StandardFileReader, self).__init__(file_)
        self.file_type = file_type_
        # the following lists controls how they are processed
        # as_array: should values be read in as an array and output to sql as an array
        #  for example, downloads and grants are an array while relevance has several distinct values but isn't an array
        self.array_types = ('download', 'reads', 'author', 'reference', 'grants', 'citation', 'reader', 'simbad', 'ned')
        # quote_value: should individual values sent to sql be in quotes.  
        #  for example, we don't quote bibcode, but we do names of authors
        self.quote_values = ('author','simbad','grants', 'ned')
        # tab_separator: is the tab a separator in the input data
        self.tab_separated_values = ('author', 'download', 'reads')
        
    def read(self, size=-1):
        line = self._iostream.readline()
        if len(line) == 0:
            return ''
        # does the next line match the current bibcode?
        bibcode = line[:19]
        value = line[20:-1]
        match = self._bibcode_match(bibcode)

        if self.file_type in (self.array_types):
            value = [value]
        while match:
            line = self._iostream.readline()
            value.append(line[20:-1])
            match = self._bibcode_match(bibcode)
        return self.process_line(bibcode, value)
    

    def readline(self):
        line = self._iostream.readline()
        return self.process_line(line)

        
    def process_line(self, bibcode, value):
        as_array = self.file_type in self.array_types
        quote_value = self.file_type in self.quote_values
        tab_separator = self.file_type in self.tab_separated_values
        processed_value = self.process_value(value, as_array, quote_value, tab_separator)
        row = '{}\t{}\n'.format(bibcode, processed_value)
        return row
    
    def _bibcode_match(self, bibcode):
        """ peek ahead to next line for bibcode and check for mactch"""
        file_location = self._iostream.tell()
        next_line = self._iostream.readline()
        self._iostream.seek(file_location)
        next_bib = next_line[:19]
        if bibcode == next_bib:
            return True
        return False

        
    def process_value(self, value, as_array=False, quote_value=False, tab_separator=False):
        """convert value to what Postgres will accept"""
        if '\x00' in value:
            # postgres does not like nulls in strings
            self.logger.error('in columnFileIngest.process_value with null value in string: {}', value)
            value = value.replace('\x00', '')
    
        return_value = ''
        if tab_separator and isinstance(value, list) and len(value) == 1:
            value = value[0]
    
        output_separator = ','
        if (as_array == False):
            output_separator = '\t'
    
        if isinstance(value, str) and '\t' in value:
            # tab separator in string means we need to create a sql array
            values = value.split('\t')
            # should check for double quotes in names
            for v in values:
                if quote_value and v[0] != '"':
                    v = '"' + v + '"'
                if len(return_value) == 0:
                    return_value = v
                else:
                    return_value += output_separator + v
                
        elif isinstance(value, list):
            # array of values to conver to sql 
            for v in value:
                v = v.replace('\t', ' ')
                if quote_value and v[0] != '"':
                    v = '"' + v + '"'
                if len(return_value) == 0:
                    return_value = v 
                else:
                    return_value += output_separator + v
    
        elif isinstance(value, str):
            if quote_value and value[0] != '"':
                return_value = '"' + value + '"'
            else:
                return_value = value
    
        if as_array:
            # postgres array are contained within curly braces
            return_value = '{' + return_value + '}'
        return return_value


        
       
        