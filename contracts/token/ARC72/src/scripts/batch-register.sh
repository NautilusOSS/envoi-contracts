for i in $( cat reserved | grep -v -e '#' )
do
 echo ${i}
 node main.js registrar register --apid 797609 --name ${i} --owner BRB3JP4LIW5Q755FJCGVAOA4W3THJ7BR3K6F26EVCGMETLEAZOQRHHJNLQ --duration  5 --debug
done
