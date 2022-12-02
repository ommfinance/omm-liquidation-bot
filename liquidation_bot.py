import json
import concurrent.futures
import time

from utils import *


def is_collateral_enabled(collateral_address) -> bool:
    reserve_data = get_reserve_data(collateral_address)
    if reserve_data.get('usageAsCollateralEnabled') == '0x1':
        return True
    return False


class Liquidation:
    def __init__(self):
        super(Liquidation, self).__init__()
        self.liquidation_address = []
        self.tx_hashes = []
        self.liquidation_list = []
        self.wallets = []

    def get_wallets(self, index):
        borrow_wallets = get_borrow_wallets(index)
        self.wallets.extend(borrow_wallets)
        if len(borrow_wallets) == 50:
            self.get_wallets(index + 1)

    def fetch_borrow_wallets(self):
        return self.get_wallets(0)

    def fetch_user_borrow_wallet(self, borrow_wallet):
        self.wallets = borrow_wallet

    def sort_list(self):
        return sorted(self.liquidation_list, key=lambda i: i['badDebt'], reverse=True)

    def get_liquidation_list(self, address):
        _healthFactor = int(get_health_factor(address), 0)
        if _healthFactor < 10 ** 18 and _healthFactor != -1:
            _user_data = get_user_liquidation_data(address)
            if _user_data.get('collaterals'):
                self.liquidation_list.append(_user_data)


    def liquidate(self):
        sorted_list = self.sort_list()
        for ids, value in enumerate(sorted_list):
            # print(value)
            bad_debt: int = value.get('badDebt')
            borrow_info: dict = value.get('borrows')
            collateral_info: dict = value.get('collaterals')
            address = value.get('address')

            borrow_value, collateral_value, amount_to_liquidate = 0, 0, 0
            borrow_coin, collateral_coin = "", ""
            for key, values in borrow_info.items():
                _value = int(values.get('maxAmountToLiquidateUSD'), 0)
                if borrow_value < _value:
                    borrow_value = _value
                    amount_to_liquidate = int(values.get('maxAmountToLiquidate'), 0)
                    borrow_coin = key

            for key, values in collateral_info.items():
                if not is_collateral_enabled(collaterals.get(coins_name.get(key))):
                    continue
                _value = int(values.get('underlyingBalanceUSD'), 0)
                if collateral_value < _value:
                    collateral_value = _value
                    collateral_coin = key

            liquidate_token_address = collaterals.get(coins_name.get(borrow_coin))
            collateral_token_address = collaterals.get(coins_name.get(collateral_coin))

            depositData = {'method': 'liquidationCall', 'params': {
                '_collateral': collateral_token_address,
                '_reserve': liquidate_token_address,
                '_user': address,
                '_purchaseAmount': amount_to_liquidate}}
            data = json.dumps(depositData).encode('utf-8')
            params = {"_to": lending_pool_contract_address,
                      "_value": amount_to_liquidate, "_data": data}

            healthFactor = int(get_health_factor(address), 0)
            fees_details = get_user_account_data(address)
            self.tx_hashes.append({'tx_hash': liquidate(liquidate_token_address, params),
                                   'beforeLiquidationData': value,
                                   'healthFactorBeforeLiquidation': healthFactor,
                                   'beforeTotalBorrowsFees': fees_details,
                                   'address': address})

    def save_txn_info(self):
        for txn in self.tx_hashes:
            print("---Getting info from a transaction. ----")
            txHash = txn.get('tx_hash')
            address = txn.get('address')
            print(f"Txn Hash : {txn.get('tx_hash')}")
            tx_result = get_tx_result(txHash)

            filename = f"{int(time.time())}_liquidation.json"
            jsonData = {}
            if tx_result.get('status') == 1:
                print('---Writing Liquidation Info on a JSON File---')
                # Opening JSON file
                try:
                    with open(filename, 'r') as outfile:
                        jsonData = json.load(outfile)
                except IOError:
                    pass

                jsonData['txHash'] = txHash
                jsonData['data'] = {'healthFactorBeforeLiquidation': txn.get("healthFactorBeforeLiquidation"),
                                    'beforeLiquidationData': txn.get('beforeLiquidationData'),
                                    'beforeTotalBorrowsFees': txn.get('beforeTotalBorrowsFees'),
                                    'afterLiquidationData': get_user_liquidation_data(address),
                                    'healthFactorAfterLiquidation': int(get_health_factor(address), 0),
                                    'afterTotalBorrowsFees': get_user_account_data(address)}

                with open(filename, 'w') as outfile:
                    json.dump(jsonData, outfile)

                print(f"Txn Hash : {txHash} info saved to json.")

            elif tx_result.get('status') == 0:
                print('---Liquidation Failed---')

                jsonData['txHash'] = txHash

                with open(filename, 'w') as outfile:
                    json.dump(jsonData, outfile)
                    print(f"Txn Hash : {txHash} info saved to json.")


if __name__ == "__main__":
    instance = Liquidation()

    # get all borrowers
    # instance.fetch_borrow_wallets()

    # custom borrowers
    instance.fetch_user_borrow_wallet(['hx4818f8bc679c28ce379d4bbca5de202a7b766233'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        executor.map(instance.get_liquidation_list, instance.wallets)
    instance.liquidate()
    instance.save_txn_info()
