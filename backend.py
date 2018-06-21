#!/usr/bin/env python

import sys
from pymongo import MongoClient

# Config
mongo_host = "127.0.0.1"
mongo_port = 27017
mongo_db = "dns"
mongo_collation = "records"


class Lookup(object):
    ttl = 30

    def __init__(self, query):
        (_type, qname, qclass, qtype, _id, ip) = query
        self.has_result = False
        qname_lower = qname.lower()

        self.results = []

        client = MongoClient(mongo_host, mongo_port, connect=False)
        db = client[mongo_db]
        coll = db[mongo_collation]

        if qtype == "ANY":
            records = coll.find({"name": qname_lower})
        else:
            records = coll.find({"type": qtype, "name": qname_lower})

        if records:
            for record in records:
                if record['type'] == "SOA":
                    """
                    {
                     "name":"example.org",
                     "type":"SOA",
                     "content":"",
                     "ttl": 300,
                     "primary": "ns1.example.org",
                     "mail": "admin.example.org",
                     "serial": 2018030311,
                     "refresh": 86400,
                     "retry": 7200,
                     "expire": 3600000,
                     "nttl": 3600 
                    }
                    """
                    try:
                        self.results.append(
                            'DATA\t%s\t%s\t%s\t%s\t-1\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % ( qname_lower,
                                                                                       qclass,
                                                                                       qtype,
                                                                                       record['ttl'],
                                                                                       record['primary'],
                                                                                       record['mail'],
                                                                                       record['serial'],
                                                                                       record['refresh'],
                                                                                       record['retry'],
                                                                                       record['expire'],
                                                                                       record['nttl']
                                                                                     ))
                        self.has_result = True
                    except:
                        self.results.append('LOG\t %s SOA Record currupt maybe fields are missing.' % qname_lower)
                else:
                    """
                    {
                     "name":"www.example.org",
                     "type":"A",
                     "ttl": 300,
                     "content": "1.1.1.1"
                    }
                    """
                    self.results.append('DATA\t%s\t%s\t%s\t%d\t-1\t%s' % (
                    qname_lower, qclass, record['type'], record['ttl'], record['content']))
                    self.has_result = True

    def str_result(self):
        if self.has_result:
            return '\n'.join(self.results)
        else:
            return ''


class DNSbackend(object):

    def __init__(self, filein, fileout):
        self.filein = filein
        self.fileout = fileout

        self._process_requests()

    def _fprint(self, message):
        self.fileout.write(message + '\n')
        self.fileout.flush()

    def _process_requests(self):
        first_time = True

        while 1:
            rawline = self.filein.readline()

            if rawline == '':
                return

            line = rawline.rstrip()

            if first_time:
                if line == 'HELO\t1':
                    self._fprint('OK\tPython backend ready.')
                else:
                    rawline = self.filein.readline()
                    sys.exit(1)
                first_time = False
            else:
                query = line.split('\t')
                if len(query) != 6:
                    self._fprint('LOG\tPowerDNS sent unparseable line')
                    self._fprint('FAIL')
                else:
                    lookup = Lookup(query)
                    if lookup.has_result:
                        pdns_result = lookup.str_result()
                        self._fprint(pdns_result)
                    self._fprint('END')


if __name__ == "__main__":
    infile = sys.stdin
    outfile = sys.stdout

    try:
        DNSbackend(infile, outfile)

    except:
        raise
