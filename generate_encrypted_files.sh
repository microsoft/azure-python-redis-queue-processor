echo "This will create new AES key and update files in Azure and locally."
echo "Do you want to continue? [y/n]"
read choice

if [[ $choice = y ]]
then
    export PYTHONPATH=.
    python samples/generateEncryptedFiles.py
    read -p "Press any key to exit..."
fi
