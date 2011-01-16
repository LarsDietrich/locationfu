#!/bin/bash

clean() {
    echo -e "\nCleaning up existing minified files..."
    find . -name \*.min.js -exec rm {} \;
    find . -name \*.min.css -exec rm {} \;
}

minify() {
    if ! [ `find . -type f -name yuicompressor\*.jar` ]
    then
        echo "Unable to locate the YUI Compressor jar file!"
        exit 1
    else 
        YUICOMPRESSOR=`find . -type f -name yuicompressor\*.jar`
fi

    echo -e "\nMinifing JavaScript..."
    jslist=`find . -type f -name \*.js`
    for jsfile in $jslist
    do
        echo "Processing: ${jsfile}"
        java -jar ${YUICOMPRESSOR} -o ${jsfile%.*}.min.js ${jsfile}
    done
    
    echo -e "\nMinifing CSS..."
    csslist=`find . -type f -name \*.css`
    for cssfile in $csslist
    do
        echo "Processing: ${cssfile}"
        java -jar ${YUICOMPRESSOR} -o ${cssfile%.*}.min.css ${cssfile}
    done
}

deploy() {
    echo -e "\nDeploying to App Engine"
    appcfg.py --no_cookies update .
}

JUSTMIN=0
JUSTCLEAN=0

while getopts "mc" input
do
    case $input in
        m ) JUSTMIN=1;;
        c ) JUSTCLEAN=1;;
    esac
done

if [ $JUSTMIN -eq 1 ]
then
    minify
    exit 0
fi

if [ $JUSTCLEAN -eq 1 ]
then
    clean
    exit 0
fi

clean
minify
deploy
clean
exit 0
