# Loading virtual environment
python3 -m venv venv
source venv/bin/activate

# Installing packages
pip3 install --upgrade pip3
pip3 install -r requirements.txt
nodeenv -p
npm install -g chart.js --save