echo "This will create new AES key and update files in Azure and locally."
echo "Do you want to continue?"
read choice

if [[ $choice = y ]]
then
    set PYTHONPATH=.
    python scripts/GenerateEncryptedFiles.py
    read -p "Press any key to exit..."
fi
