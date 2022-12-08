private_key = "---private_key---"

score_address_provider = '---address_provider_address---'
# Coins Value {"tokenName": "scoreName"}
coins_name = {"ICX": "sICX",
              "USDC": "IUSDC",
              "USDS": "USDS",
              "OMM":"OMM",
              "bnUSD":"bnUSD",
              "BALN":"BALN"}


# Networks
connections = {
    "mainnet": {"iconservice": "https://ctz.solidwallet.io", "nid": 1},
    "sejong": {"iconservice": "https://sejong.net.solidwallet.io", "nid": 83},
    "lisbon": {"iconservice": "https://lisbon.net.solidwallet.io", "nid": 2},
    "berlin": {"iconservice": "https://berlin.net.solidwallet.io", "nid": 7}}

network = "mainnet"  # set this to one of mainnet, sejong, lisbon, berlin, or custom
env = connections[network]
