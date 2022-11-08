#!/bin/bash

HAVE_TUNNEL='netstat -natp \| grep 43000 \| grep ESTABLISHED \| grep ssh \| wc -l'

ITERATIONS=0

while [ true ]; do 
	ITERATIONS=$( expr $ITERATIONS + 1 )
	X=`$HAVE_TUNNEL`
	echo "$ITERATIONS : $X"
	if [[ $( echo "$X" | wc -l ) -ge "2" ]]; then
		PID="$( pgrep -f "ssh -fN -L 42069:localhost:42069 root@localhost -p 43000" )"
		if [[ ! $PID ]]; then
			ssh -fN -L 42069:localhost:42069 root@localhost -p 43000
		fi
	fi
	sleep 10
done
