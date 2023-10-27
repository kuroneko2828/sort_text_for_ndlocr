dir="$1"
if [ $# -ne 1 ]; then
	echo "geve dir_name"
	exit
fi

current_dir= pwd
cd ${dir}
ls -F | grep -v / | awk '{ printf "mv %s R%07d.jpg\n", $0, NR}' | sh
cd ${current_dir}
