from flask import Flask, render_template, request, redirect
import os
from time import time
from wallet import Account, Wallet
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json

def firebaseInitialization():
    cred = credentials.Certificate("config/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://blockchain-wallet-a2812-default-rtdb.firebaseio.com'})
    print("🔥🔥🔥🔥🔥 Firebase Connected! 🔥🔥🔥🔥🔥")

firebaseInitialization()

STATIC_DIR = os.path.abspath('static')

app = Flask(__name__, static_folder=STATIC_DIR)
app.use_static_for_root = True

ref = db.reference('adminAccount/')
account= ref.get()
if(not account):
    account = Account()

myWallet =  Wallet()


@app.route("/", methods= ["GET", "POST"])
def index():
    global account, myWallet
      
    isConnected = myWallet.checkConnection()
    balance = "No Balance"
    transactions={    }
    address = None
    if(account):
        if(type(account)==dict):
            balance = myWallet.getBalance(account['address'])
            transactions = myWallet.getTransactions(account['address'])
            address= account['address']
        else:
            balance = myWallet.getBalance(account.address)
            transactions = myWallet.getTransactions(account.address)
            address= account.address
    
    amountList = []
    colorList=[]
    indicesTransactions = []

    # reverse the transactions list and store it in reverseTransactions
    reverseTransactions = transactions[::-1]

    # loop over reverseTransactions
    for index, transaction in enumerate(transactions):
        
        colorList.append("red" if transaction["from"] == address else "blue")
        # Append the amount in amountList
        amountList.append(transaction)
        # Append index in indicesTransactions
        indicesTransactions.append(index)
    traceTnx = {
        'x': indicesTransactions,
        'y': amountList,
        'name': 'Amount',
        'type': 'bar',
        'marker': { 'color' : colorList }
    }

    # Assign correct labels to x and y axis
    layoutTnx = {
        'title': 'Transaction History',
        'xaxis': { 'title': 'Transactions' },
        'yaxis': { 'title': 'Amount(ETH)' }
    }

    transactionData ={
            'trace': [traceTnx], 
            'layout': layoutTnx
            }
    
    transactionData = json.dumps(transactionData)

    return render_template('index.html', isConnected=isConnected,  account= account, balance = balance, transactionData = transactionData)

   
@app.route('/transactions')
def transactions():
    global account, myWallet    
    transactions = None
    if(type(account)==dict):
         transactions = myWallet.getTransactions(account['address'])
    else:
         transactions = myWallet.getTransactions(account.address)

    return render_template('transactions.html', account=account, transactions= transactions)

@app.route("/makeTransaction", methods = ["GET", "POST"])
def makeTransaction():
    global myWallet, account

    senderType = 'ganache'
    accountAddress = None
    privateKey = None
    if(type(account)==dict):
        accountAddress = account['address']
        privateKey = account['privateKey']
    else:
        accountAddress = account.address
        privateKey = account.privateKey

    sender =accountAddress
    receiver = request.form.get("receiverAddress")
    amount = request.form.get("amount")

    if(sender == accountAddress):
        senderType = 'newAccountAddress'

    tnxHash= myWallet.makeTransactions(sender, receiver, amount, senderType, privateKey)
    myWallet.addTransactionHash(tnxHash, sender, receiver, amount)
    return redirect("/")

if __name__ == '__main__':
    app.run(debug = True, port=4000)
