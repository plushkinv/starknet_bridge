from statistics import mean
import time
from web3 import Web3
import requests
import random
from datetime import datetime
import config
import fun
from fun import *


ethBridgeAddress = '0xae0ee0a63a2ce6baeeffe56e7714fb4efe48d419'

ethBridgeAbi = [
    {
        "type":"function",
        "name":"deposit",
        "inputs": [
            {"name":"amount","type":"uint256"},
            {"name":"l2Recipient","type":"uint256"}
        ]
    },
    {
        "type":"function",
        "name":"withdraw",
        "inputs": [
            {"name":"amount","type":"uint256"},
            {"name":"recipient","type":"address"}
        ]
    },
]


current_datetime = datetime.now()
print(f"\n\n {current_datetime}")
print(f'============================================= Плюшкин Блог =============================================')
print(f'subscribe to : https://t.me/plushkin_blog \n============================================================================================================\n')

keys_list = []
with open("private_keys.txt", "r") as f:
    for row in f:
        private_key=row.strip()
        if private_key:
            keys_list.append(private_key)

random.shuffle(keys_list)
i=0
for private_line in keys_list:
    string_list = private_line.split("	")
    private_key = string_list[0]
    wallet_out = string_list[1]    
    i+=1
    if config.proxy_use:
        while True:
            try:
                requests.get(url=config.proxy_changeIPlink)
                fun.timeOut("teh")
                result = requests.get(url="https://yadreno.com/checkip/", proxies=config.proxies)
                print(f'Ваш новый IP-адрес: {result.text}')
                break
            except Exception as error:
                print(
                    ' !!! Не смог подключиться через Proxy, повторяем через 2 минуты... ! Чтобы остановить программу нажмите CTRL+C или закройте терминал')
                time.sleep(120)

    try:
        web3 = Web3(Web3.HTTPProvider(config.rpc_links['ETH'], request_kwargs=config.request_kwargs))
        account = web3.eth.account.from_key(private_key)
        wallet = account.address    
        log(f"I-{i}: Начинаю работу с {wallet}")
        balance = web3.eth.get_balance(wallet)
        balance_decimal = Web3.from_wei(balance, 'ether')        

        while True:
            gasPrice = web3.eth.gas_price
            gasPrice_Gwei = Web3.from_wei(gasPrice, 'Gwei')
            log(f"gasPrice_Gwei = {gasPrice_Gwei}")
            if config.max_gas_price > gasPrice_Gwei:
                break
            else:
                log("Жду снижения цены за газ")
                timeOut("teh")
                timeOut("teh")
                timeOut("teh")



        maxPriorityFeePerGas = web3.eth.max_priority_fee
        fee_history = web3.eth.fee_history(10, 'latest', [10, 90])
        baseFee=round(mean(fee_history['baseFeePerGas']))
        maxFeePerGas = maxPriorityFeePerGas + round(baseFee * config.gas_kef)
        
        
        komissia = maxFeePerGas * 120000
        if config.bridge_all_money:
            value = int(balance - komissia) # сумма которая будет отправлена в самой транзакции. в нее войдет комиссия моста
        else:
            value_decimal = random.randint(int(config.bridge_min*100000000),int(config.bridge_max*100000000))/100000000
            value = web3.to_wei(value_decimal, 'ether') 

        amount = int(value - 0.2*komissia)  # сколько хотим получить на выходе

        print(f"balance {Web3.from_wei(balance, 'ether')}")
        print(f"value_decimal {value_decimal}")
        print(f"value {Web3.from_wei(value, 'ether')}")
        print(f"komissia за транзакцию = {Web3.from_wei(komissia, 'ether')}")
        print(f"amount = {Web3.from_wei(amount, 'ether')}")

        if balance_decimal < config.minimal_need_balance or balance < value + komissia:
            log("Недостаточно эфира.  жду когда пополнишь. на следующем круге попробую снова")
            fun.save_wallet_to("no_money_wa", wallet)
            keys_list.append(private_line)            
            timeOut("teh")
            continue  

        dapp_contract = web3.eth.contract(address=web3.to_checksum_address(ethBridgeAddress), abi=ethBridgeAbi)
        transaction = dapp_contract.functions.deposit(
                            amount,  
                            int(wallet_out[2:],base=16)
                        ).build_transaction({
                            'from': wallet,
                            'value': value,
                            'maxFeePerGas': maxFeePerGas,
                            'maxPriorityFeePerGas': maxPriorityFeePerGas,            
                            'nonce': web3.eth.get_transaction_count(wallet),
                        })

        

        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = web3.to_hex(web3.eth.send_raw_transaction(signed_txn.rawTransaction))
        tx_result = web3.eth.wait_for_transaction_receipt(txn_hash)

        if tx_result['status'] == 1:
            log_ok(f'bridge OK: {txn_hash}')
            save_wallet_to("bridge_ok_pk", private_line)
            fun.delete_private_key_from_file("private_keys", private_line)
            fun.delete_wallet_from_file("no_money_wa", wallet)
            fun.delete_wallet_from_file("bridge_false_pk", private_line)
        else:
            log_error(f'bridge false: {txn_hash}')
            save_wallet_to("bridge_false_pk", private_line)
            fun.delete_wallet_from_file("no_money_wa", wallet)
            keys_list.append(private_line)   

        timeOut()


    except Exception as error:
        fun.log_error(f'bridge false: {error}')    
        save_wallet_to("bridge_false_pk", private_line)
        keys_list.append(private_line)
        timeOut("teh")
        continue


        
  
    
log("Ну типа все, кошельки закончились!")        

