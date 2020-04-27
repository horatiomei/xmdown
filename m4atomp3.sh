#!/bin/sh
for i in *.m4a; do
	echo "converting: ${i%.m4a}.mp3"
	faad -o - "$i" | lame --resample 44.1 -b 64kbps - "${i%.m4a}.mp3"
done


