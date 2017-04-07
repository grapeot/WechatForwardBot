DedupAndCopyFile() {
    LC_ALL=C md5sum $1/*.gif | sort -k1,1 -u | awk '{print $2;}' | sed 's/^.*\///' > files.txt
    rsync -av --files-from=files.txt $1 dat/gifs
    rm files.txt
}

DedupAndCopyFile '../HistoryImages'

# Convert to jpg for training use
ls ./dat/gifs | xargs -n1 -I{} -P4 bash -c 'echo {}; if [ ! -e "dat/jpgs/{}.jpg" ]; then convert "dat/gifs/{}[0]" "dat/jpgs/{}.jpg"; fi'
# Generate files list for Caffe use
find dat/jpgs > files.txt
