# --------------------------------------------------------------------
# Test cfa
# --------------------------------------------------------------------
sample_files=$PWD

test_file=delme_cfa.nc
test_dir=delme_cfa_dir

mkdir -p $test_dir

for opt in vs vm vc
do
  cfa    -$opt $sample_files/*[np][cp] >/dev/null
  cfa -1 -$opt $sample_files/*[np][cp] >/dev/null
  for f in `ls $sample_files/*.[np][cp] | grep -v $test_file`
  do
#    echo $f
    cfa -$opt $f >/dev/null
    if [ $opt = vs ] ; then
      cfa --overwrite -o $test_file $f
      cfa --overwrite -d $test_dir  $f
    fi
  done
  rm -f $test_file
done

rm -f $test_file
cfa --overwrite -d $test_dir  $sample_files/*.[np][cp]

rm -f $test_file
cfa -o $test_file $sample_files/test*.[np][cp]

rm -f $test_file
cfa -o $test_file $test_dir

rm -fr $test_dir $test_file

