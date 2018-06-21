# powerdns_mongodb_backend

More informations on: https://lanbugs.de/howtos/python-co/powerdns-mongodb-backend/

The schema for the collection in mongoDB is:

for SOA record:

...
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
...

for all other records:

...
{
 "name":"www.example.org",
 "type":"A",
 "ttl": 300,
 "content": "1.1.1.1"
}
...

