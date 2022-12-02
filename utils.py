from iconsdk.icon_service import IconService
from iconsdk.exception import JSONRPCException
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.builder.transaction_builder import CallTransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from repeater import retry
from consts import *

deployer_wallet = KeyWallet.load(bytes.fromhex(private_key))

icon_service = IconService(HTTPProvider(env["iconservice"], 3))
NID = env["nid"]


@retry(JSONRPCException, tries=10, delay=1, back_off=2)
def get_tx_result(_tx_hash):
    _tx_result = icon_service.get_transaction_result(_tx_hash)
    return _tx_result


def get_all_address() -> dict:
    _call = CallBuilder() \
        .from_(deployer_wallet.get_address()) \
        .to(score_address_provider) \
        .method("getAllAddresses") \
        .build()
    _result = icon_service.call(_call)
    return _result


# Get contract addresses
addresses = get_all_address()

collaterals = addresses.get('collateral')
lending_pool_contract_address = addresses['systemContract']['LendingPool']
lending_pool_data_provider_contract_address = addresses['systemContract']['LendingPoolDataProvider']
staking_contract = addresses['systemContract']['Staking']


def get_borrow_wallets(index: int):
    _params = {"_index": index}
    _call = CallBuilder() \
        .from_(deployer_wallet.get_address()) \
        .to(lending_pool_contract_address) \
        .method("getBorrowWallets") \
        .params(_params) \
        .build()
    return icon_service.call(_call)


@retry(Exception, tries=5, delay=1)
def get_health_factor(_address) -> str:
    _params = {"_user": _address}
    _call = CallBuilder() \
        .from_(deployer_wallet.get_address()) \
        .to(lending_pool_data_provider_contract_address) \
        .method("getUserAccountData") \
        .params(_params) \
        .build()
    _result = icon_service.call(_call)
    return _result['healthFactor']


@retry(Exception, tries=5, delay=1)
def get_user_liquidation_data(_address) -> dict:
    _params = {"_user": _address}
    _call = CallBuilder() \
        .from_(deployer_wallet.get_address()) \
        .to(lending_pool_data_provider_contract_address) \
        .method("getUserLiquidationData") \
        .params(_params) \
        .build()
    _result = icon_service.call(_call)
    _result["address"] = _address
    return _result

def get_reserve_data(address):
    _params = {"_reserve" :address}
    _call = CallBuilder() \
        .from_(deployer_wallet.get_address()) \
        .to(lending_pool_data_provider_contract_address) \
        .method("getReserveData") \
        .params(_params) \
        .build()
    return icon_service.call(_call)


def get_user_account_data(_address) -> dict:
    _params = {"_user": _address}
    _call = CallBuilder() \
        .from_(deployer_wallet.get_address()) \
        .to(lending_pool_data_provider_contract_address) \
        .method("getUserAccountData") \
        .params(_params) \
        .build()
    _result = icon_service.call(_call)
    return _result


def get_user_reserve_data(_address, token_address) -> dict:
    _params = {"_user": _address, '_reserve': token_address}
    _call = CallBuilder() \
        .from_(deployer_wallet.get_address()) \
        .to(lending_pool_data_provider_contract_address) \
        .method("getUserReserveData") \
        .params(_params) \
        .build()
    _result = icon_service.call(_call)
    return _result


def get_today_rate() -> dict:
    _params = {}
    _call = CallBuilder() \
        .from_(deployer_wallet.get_address()) \
        .to(staking_contract) \
        .method("getTodayRate") \
        .params(_params) \
        .build()
    _result = icon_service.call(_call)
    return _result


def liquidate(liquidate_token_address, params):
    call_transaction = CallTransactionBuilder() \
        .from_(deployer_wallet.get_address()) \
        .to(liquidate_token_address) \
        .nid(NID) \
        .step_limit(100_000_00_000) \
        .nonce(100) \
        .method("transfer") \
        .params(params) \
        .build()
    signed_transaction = SignedTransaction(call_transaction, deployer_wallet)
    tx_hash = icon_service.send_transaction(signed_transaction)
    return tx_hash
