#!/bin/bash

temp="${HOME}/AX/venv/bots/karutag/temp/"
card_in="${temp}card.webp"
card_out="${temp}card.out"
text="${temp}text"


thegrep=$(file "${temp}card.webp" | grep "836 x 419")

if [[ -z "$thegrep" ]];
then
    echo "nope"
    exit 0
fi


magick -extract 180x49+50+57 $card_in $card_out &> /dev/null
tesseract $card_out $text &> /dev/null
cards=$(cat "${text}.txt")

magick -extract 180x49+317+57 $card_in $card_out &> /dev/null
tesseract $card_out $text &> /dev/null
cards="${cards} $(cat "${text}.txt")"

magick -extract 180x49+590+57 $card_in $card_out &> /dev/null
tesseract $card_out $text &> /dev/null
cards="${cards} $(cat "${text}.txt")"

echo $cards

