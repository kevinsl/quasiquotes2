

def decode(s):
    print 'in qq_decode with ', s
    return qq_transform_string(s), None


class IncrementalDecoder(utf_8.IncrementalDecoder):
    def __init__(self, *args, **kwargs):
        print 'okok'
    #pass
    #def decode(self, input, final=False):
    #    print 'in ID.decode with ', input, final
    #    return transform_string(super(IncrementalDecoder, self).decode(input, final))


class StreamReader(utf_8.StreamReader):
    def __init__(self, *args, **kwargs):
        #super(StreamReader, self).__init__(*args, **kwargs)
        print 'in here'

        codecs.StreamReader.__init__(self, *args, **kwargs)
        self.stream = cStringIO.StringIO(qq_transform(self.stream))

        #text = args[0].read()
        #self.stream = StringIO(transform_string(text))
        #print self.stream


def search_function(encoding):
    if encoding != 'quasiquotes': return None
    # Assume utf8 encoding
    utf8=encodings.search_function('utf8')
    return codecs.CodecInfo(
        name = 'quasiquotes',
        encode = utf8.encode,
        decode = decode,
        incrementalencoder = utf8.incrementalencoder,
        incrementaldecoder = IncrementalDecoder,
        streamreader = StreamReader,
        streamwriter = utf8.streamwriter)

codecs.register(search_function)

