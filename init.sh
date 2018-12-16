# Loading virtual environment
python3 -m venv venv
source venv/bin/activate

# Installing packages
pip3 install --upgrade pip
pip3 install -r requirements.txt
nodeenv -p
cat npm-requirements.txt | xargs npm install -g