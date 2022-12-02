private_key = "c5769504c2712e1c6798291a8e1ad67d7c7d0bfa4eea9773c391ac8e158f73d6"

score_address_provider = 'cx1e6fcc68f8007b88fdde5503229d421de3b62c3a'
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

network = "sejong"  # set this to one of mainnet, sejong, lisbon, berlin, or custom
env = connections[network]
