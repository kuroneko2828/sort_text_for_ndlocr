tmpfile=$(mktemp)
python3 sort_text.py "$1" "$tmpfile" "$3"
python3 error_correction.py "$tmpfile" "$2"
rm -f "$tmpfile"