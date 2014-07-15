#!/bin/bash

# This crude script converts some cruical information from VDR channels.conf to ZAP (czap) channels.conf format. Encoding is not checked, iconv -f latin1 may be necessary.

while read line
do
  if echo "$line" | grep -qE "(Regional)|(Digital Free)|(ARD)|(ZDF)"
  then
    name=`echo "$line" | cut -d":" -f 1 | cut -d";" -f 1`
    freq=`echo "$line" | cut -d":" -f 2`
    qam=`echo "$line" | cut -d":" -f 3 | sed 's/M//'`
    srate=`echo "$line" | cut -d":" -f 5`
    vpid=`echo "$line" | cut -d":" -f 6`
    apid1=`echo "$line" | cut -d":" -f 7 | cut -d";" -f 1 | cut -d"," -f 1 | sed 's/=.*$//'`
    apid2=`echo "$line" | cut -d":" -f 7 | cut -d";" -f 2 | cut -d"," -f 1 | sed 's/=.*$//'`
    if [ "${apid1}" != "0" ]
    then
      apid=${apid1}
    else
      apid=${apid2}
    fi
    sid=`echo "$line" | cut -d":" -f 10`
    if [ "${vpid}" -gt "1" ] # filter radio
    then
      echo "${name}:${freq}000:INVERSION_AUTO:${srate}000:FEC_NONE:QAM_${qam}:${vpid}:${apid}:${sid}"
    fi
  fi
done
