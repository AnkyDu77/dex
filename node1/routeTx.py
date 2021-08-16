

def routeTx(type="common"):

    if type is "common":
        # just include tx in block
    elif type is "trade":
        # set tx in divisoin set
    elif type is "cancel":
        # cancel "trade" tx
    else:
        # send tx_type error msg
