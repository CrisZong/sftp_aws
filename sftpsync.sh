#!/bin/bash
#
# Use batch file with SFTP shell script 
# using SFTP authorized_keys
#
#############################################
#set -x

# Create SFTP batch file
tempfile="/tmp/sftpsync.$$"  
count=0

usage() { echo "Usage: $0 -i ssh_key -u username -S source_dir -H remote_host -R remote_dir" 1>&2; exit 1; }

if [ $# -eq 0 ] ; then
  usage ; 
  exit 1;
fi

while getopts "u:S:H:R:i:h" opt; do
	case ${opt} in
		u ) ### username for transfer
			user=$OPTARG
			;;
		S ) ### source directory
			source_dir=$OPTARG
			;;
		H ) ### remote server
			remote_server=$OPTARG
			;;
		R ) ### remote directory
			remote_dir=$OPTARG
			;;
		i ) ### ssh key to use
			identity_file=$OPTARG
			;;
		h | [?] ) usage ; exit;;
		esac
done
shift $((OPTIND-1))

# if any inputs are not provided, show usage
if [ ! $user ] || [ ! $source_dir ] || ! [ $remote_server ] || [ ! $remote_dir ] || [ ! $identity_file ]; then
	usage
	exit 1
fi

# remove sftp batch file
trap "/bin/rm -f $tempfile" 0 1 15      

timestamp="$source_dir/.timestamp"

echo "cd $remote_dir" >> $tempfile
# timestamp file will not be available when executed for the very first time
if [ ! -f $timestamp ] ; then   
  # no timestamp file, upload all files
  for filename in $source_dir/*
  do
    if [ -f "$filename" ] ; then
      # command to upload files in sftp batch file
      echo "put -P \"$filename\"" >> $tempfile
      # Increase the count value for every file found
      count=$(( $count + 1 ))   
    fi
  done
else   
  # If timestamp file found, look out for newer files only
  # Check for newer files based on the timestamp
  for filename in $(find $source_dir -newer $timestamp -type f -print)   
  do
    # If found newer files place the command to upload these files in batch file
    echo "put -P \"$filename\"" >> $tempfile  
    # Increase the count based on the new files
    count=$(( $count + 1 ))   
  done
fi

# If no new files, do nothing
if [ $count -eq 0 ] ; then   
  echo "$0: No files require uploading to $remote_server" >&2
  exit 1
fi
# command to exit the sftp connection in batch file
echo "quit" >> $tempfile   

echo "Synchronizing: Found $count files in local folder to upload."
# Main command to use batch file with SFTP shell script

sftp -i $identity_file -b $tempfile "$user@$remote_server"  
echo "Done. All files synchronized with $remote_server"
# Create/modify timestamp file
touch $timestamp  

# Remove the sftp batch file
rm -f $tempfile  

exit 0
