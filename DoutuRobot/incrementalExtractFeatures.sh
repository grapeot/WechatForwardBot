# Generate files.txt
awk '{ printf("dat/jpgs/%s.jpg\n", $1); }' < ./featuresall.txt | sort > extractedFiles.txt
find dat/jpgs -type f | sort > allFiles.txt
comm -23 allFiles.txt extractedFiles.txt > files.txt
rm allFiles.txt
rm extractedFiles.txt
lines=`wc -l files.txt`
echo files.txt generated, with $lines lines.

# Invoke Caffe to extract features
python3 -u ./extractFeatures.py -i files.txt -o newFeatures.txt
sed -i 's/dat\/jpgs\///' newFeatures.txt
sed -i 's/\.jpg\t/\t/' newFeatures.txt
cp featuresall.txt featuresall.txt.bak
cat newFeatures.txt >> featuresall.txt
