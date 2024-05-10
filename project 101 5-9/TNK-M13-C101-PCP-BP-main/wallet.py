from web3 import Web3
import time
from datetime import datetime
from firebase_admin import db

sepoliaUrl = "https://sepolia.infura.io/v3/7cc0d838c6304750ab8f26877179b0b3" 
web3 = Web3(Web3.HTTPProvider(sepoliaUrl))

class Account():
    def __init__(self):
        self.account = web3.eth.account.create()
        self.address = self.account.address
        self.privateKey = self.account.key.hex()
        self.addToDB(self.address, self.privateKey)
 
    def addToDB(self, address, privateKey):
        ref = db.reference("adminAccount/")
        ref.set({
            "address" : address,
            "privateKey" :privateKey
        })

class Wallet():
    def __init__(self):
        self.transactions = {}

    def checkConnection(self):
        if web3.is_connected():
           return True
        else:
            return False
        
    def makeTransactions(self, senderAddress, receiverAddress, amount, senderType, privateKey = None):
        web3.eth.defaultAccount = senderAddress
        if(senderType == 'ganache'):
            tnxHash = web3.eth.send_transaction({
                "from": senderAddress,
                "to": receiverAddress,
                "value": web3.to_wei(amount, "ether")  
                })  
        else:
            transaction = {
                "to": receiverAddress,
                "value": web3.to_wei(amount, "ether"),
                "nonce": web3.eth.get_transaction_count(senderAddress), 
                "gasPrice": web3.to_wei(10, 'gwei'),
                "gas": 21000 
            }
            signedTx = web3.eth.account.sign_transaction(transaction, privateKey)
            tnxHash = web3.eth.send_raw_transaction(signedTx.rawTransaction)
    
        return tnxHash.hex()
        
    def getBalance(self, address):
        balance = web3.eth.get_balance(address)
        return web3.from_wei(balance, 'ether')
    
    def addTransactionHash(self, tnxHash, senderAddress, receiverAddress, amount):
        ref = db.reference('transactions/' + tnxHash)
        ref.set({
            "from":senderAddress,
            "to":receiverAddress,
            "tnxHash":tnxHash,
            "amount":amount,
            "time": time.time()
        })
        
    def getTransactions(self, address):
        asSender = list(db.reference('transactions/').order_by_child('from').equal_to(address).get().values())
        asReceiver = list(db.reference('transactions/').order_by_child('to').equal_to(address).get().values())
        allUserTnx = asSender + asReceiver
        allUserTnx = sorted(allUserTnx, key=lambda txn: txn.get('time', 0), reverse=True)
        return allUserTnx