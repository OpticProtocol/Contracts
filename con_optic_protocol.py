import currency
import con_optic_lst001
import con_xoptic_lst001
import con_optic_stau_lst001
I = importlib


S = Hash(default_value=0)
L = Hash(default_value=0)
LINK = Hash(default_value=0)
metadata = Hash(default_value=0)
blockdata = Hash(default_value=0)


TAU = ForeignHash(foreign_contract='currency', foreign_name='balances')
OPTIC = ForeignHash(foreign_contract='con_optic_lst001', foreign_name='balances')
xOPTIC = ForeignHash(foreign_contract='con_xoptic_lst001', foreign_name='balances')
sTAU = ForeignHash(foreign_contract='con_optic_stau_lst001', foreign_name='balances')


@construct
def seed():
    metadata['operator'] = ctx.caller
    metadata['fees_wallet'] = 'eb9074ab07c502be35be4f447d370a79ac9feb62e849fe0272dfe93d0e4cdd48'
    metadata['initial_offer'] = 40_000_000
    metadata['base_pool'] = 50_000_000
    metadata['boost_pool'] = 200_000_000
    metadata['lens_factor'] = 0.0205
    metadata['xoptic_supply'] = 203_000_000
    metadata['optic_in_pool'] = 203_000_000
    metadata['optic_staked'] = 0
    metadata['stau_farm'] = 0
    metadata['xoptic_pledge'] = 0
    metadata['stau_staked'] = 0
    metadata['stau_farm'] = 0
    metadata['xoptic_ratio'] = 1
    metadata['rewards_fees'] = decimal('0.1')
   
    blockdata['block_emergency'] = False
    blockdata['xoptic_start'] = False
    blockdata['initial_close'] = False
    
    metadata['max_lens'] = 100
    metadata['instant_burn'] = decimal('0.03')
    metadata['nft_contract'] = 'con_optic_nft'

    metadata['emergency_contract'] = 1  

    metadata['operator_sign'] = [ctx.caller, '24f4184c9d9e8e8440067e75fb4c82d44c51c529581dd40e486a0ca989639600', 'b1c4b6a0baa3cef7fd57a191d3fe0798748b439ddf566825a2b614eb250bb519']

    currency.approve(999_999_999_999_999_999, ctx.this)


@export
def initial_rewards(to: str, amount: float):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    con_optic_lst001.transfer_from(amount, to, metadata['operator'])
    return amount


@export
def initial(amount: float):
    assert blockdata['initial_close'] == False, 'Initial Deposit Closed'
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must send something.'
    assert TAU[user] >= amount, 'Not enough coins to send!'
    currency.transfer_from(amount, metadata['operator'], user)
    day = now.day
    metadata['total_initial'] += amount
    metadata['initial', day] += amount
    S[user, 'initial'] += amount
    return amount


@export
def remove_initial(amount: float):
    block_emergency()
    assert blockdata['initial_close'] == False, 'Remove Locked'
    user = ctx.caller
    assert amount > 0, 'You must remove something.'
    assert S[user, 'initial'] >= amount, 'Not enough coins to remove!'
    currency.transfer_from(amount, user, metadata['operator'])
    metadata['total_initial'] -= amount
    day = now.day
    metadata['initial', day] -= amount
    S[user, 'initial'] -= amount
    return amount


@export
def claim_forge():
    assert blockdata['initial_close'] == True, 'Claim Locked'
    user = ctx.caller
    assert S[user, 'initial'] > 0, 'Not enough coins to claim!'
    amount = S[user, 'initial'] * metadata['initial_offer']  /  metadata['total_initial']
    con_optic_lst001.transfer_from(amount, user, metadata['operator'])
    S[user, 'initial'] = 0
    return amount


@export
def stake(amount: float):
    block_emergency()
    assert blockdata['xoptic_start'] == True, 'Deposit not start'
    user = ctx.caller
    assert amount > 0, 'You must stake something.'
    assert OPTIC[user] >= amount, 'Not enough coins to stake!'
    X_SUPPLY = metadata['xoptic_supply']
    OPTIC_IN_POOL = metadata['optic_in_pool']
    RECEIVED = amount / (OPTIC_IN_POOL + amount) * X_SUPPLY
    con_optic_lst001.transfer_from(amount, metadata['operator'], user)
    con_xoptic_lst001.transfer_from(RECEIVED, user, metadata['operator'])
    metadata['optic_in_pool'] += amount
    metadata['xoptic_supply'] -= RECEIVED
    metadata['xoptic_ratio'] = metadata['optic_in_pool'] / metadata[
        'xoptic_supply']
    metadata['optic_staked'] += amount
    metadata['xoptic_staked'] += RECEIVED
    S[user, 'xoptic'] += RECEIVED
    return RECEIVED


@export
def unstake(amount: float):
    block_emergency()
    assert blockdata['xoptic_start'] == True, 'Remove not start'
    user = ctx.caller
    assert amount > 0, 'You must withdrawal something.'
    assert xOPTIC[user] >= amount, 'Not enough coins to withdrawal!'
    OPTIC_OUT = amount / metadata['xoptic_supply'] * metadata[
        'optic_in_pool']
    con_xoptic_lst001.transfer_from(amount, metadata['operator'], user)
    metadata['optic_in_pool'] -= OPTIC_OUT
    metadata['xoptic_burned'] += amount
    metadata['xoptic_ratio'] = metadata['optic_in_pool'] / metadata[
        'xoptic_supply']
    metadata['optic_staked'] -= OPTIC_OUT
    metadata['xoptic_staked'] -= amount
    S[user, 'xoptic'] -= amount
    return OPTIC_OUT


@export
def claim_unstake_xoptic():
    block_emergency()
    user = ctx.caller
    amount = S[user, 'xoptic_unstake']
    assert amount > 0, 'You must unstake something.'
    con_optic_lst001.transfer_from(amount, user, metadata['operator'])
    S[user, 'xoptic_unstake'] = 0
    return amount


@export
def add_unstake_xoptic(to: str, amount: float, uid: str):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    S[to, 'xoptic_unstake'] += amount
    return amount


@export
def split(amount: float):
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must stake something.'
    assert TAU[user] >= amount, 'Not enough coins to send!'
    #currency.transfer_from(amount, metadata['operator'], user)
    currency.transfer_from(amount, ctx.this, user)
    con_optic_stau_lst001.transfer_from(amount, user, metadata['operator'])
    metadata['stau_split'] += amount
    return amount


@export
def redeem_instant(amount: float):
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must stake something.'
    assert sTAU[user] >= amount, 'Not enough sTAU to send!'
    con_optic_stau_lst001.transfer_from(amount, metadata['operator'], user)
    BURN = amount * metadata['instant_burn']

    currency.transfer_from(amount - BURN, user, ctx.this)
    currency.transfer_from(BURN, metadata['fees_wallet'], ctx.this)

    #currency.transfer_from(amount - BURN, user, metadata['operator'])
    #currency.transfer_from(BURN, metadata['fees_wallet'], metadata['operator'])
    metadata['stau_split'] -= amount
    metadata['burn'] += BURN
    return amount


@export
def redeem_slow(amount: float):
    block_emergency() 
    user = ctx.caller
    assert amount > 0, 'You must stake something.'
    assert sTAU[user] >= amount, 'Not enough sTAU to send!'
    con_optic_stau_lst001.transfer_from(amount, metadata['operator'], user)
    metadata['stau_split'] -= amount
    return amount


@export
def claim_merge_slow():
    block_emergency()
    user = ctx.caller
    amount = S[user, 'merge']
    assert amount > 0, 'You must claim something.'
    #currency.transfer_from(amount, user, metadata['operator'])
    currency.transfer_from(amount, user, ctx.this)
    S[user, 'merge'] = 0
    return amount


@export
def add_merge_slow(to: str, amount: float, uid: str):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    S[to, 'merge'] += amount

    return amount


@export
def farm(amount: float):
    block_emergency()
    user = ctx.caller
    assert blockdata['xoptic_start'] == True, 'Deposit not start'
    assert amount > 0, 'You must stake something.'
    assert sTAU[user] >= amount, 'Not enough coins to stake!'
   
    con_optic_stau_lst001.transfer_from(amount, metadata['operator'], user)

    if S[user, 'start_farm'] is None:
        S[user, 'start_farm'] = now
    metadata['stau_farm'] += amount
    S[user, 'farm'] += amount
    return S[user, 'start_farm']


@export
def remove(amount: float):
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must withdrawal something.'
    assert S[user, 'farm'] >= amount, 'Not enough coins to withdrawal!'
    con_optic_stau_lst001.transfer_from(amount, user, metadata['operator'])
    metadata['stau_farm'] -= amount
    S[user, 'farm'] -= amount
    if S[user, 'farm'] == 0:
        S[user, 'start_farm'] = None


@export
def pledge(amount: float):
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must pledged something.'
    assert xOPTIC[user] >= amount, 'Not enough coins to pledged!'
    con_xoptic_lst001.transfer_from(amount, metadata['operator'], user)
    MAX_LENS = 0
    metadata['xoptic_pledge'] += amount
    metadata['xoptic_staked'] -= amount
    S[user, 'xoptic_pledge'] += amount

    if not S[user, 'start_lens'] or S[user, 'start_lens'] is None:
        S[user, 'start_lens'] = now

    if S[user, 'lens'] == 0 or S[user, 'lens'] is None:
        S[user, 'lens'] = 0
        S[user, 'lens_time'] = now

    else:
        if S[user, 'nft_active'] or S[user, 'nft_active'] is not None:
            thing_info = I.import_module(metadata['nft_contract'])
            uid = S[user, 'nft_active']
            active = thing_info.get_boost_owner(user, uid)
            MAX_LENS = 100 * active

        lens = S[user, 'xoptic_pledge'] * (metadata['lens_factor'] / (
            60 * 60)) * (now - S[user, 'lens_time']).seconds
        if lens + S[user, 'lens'] >= S[user, 'xoptic_pledge'] * (metadata
            ['max_lens'] + MAX_LENS):
            metadata['total_lens'] += lens + S[user, 'lens'] - S[user,
                'xoptic_pledge'] * (metadata['max_lens'] + MAX_LENS)
            S[user, 'lens'] = S[user, 'xoptic_pledge'] * (metadata[
                'max_lens'] + MAX_LENS)
            S[user, 'lens_time'] = now
        else:
            S[user, 'lens'] += lens
            metadata['total_lens'] += lens
            S[user, 'lens_time'] = now



@export
def unpledge(amount: float):
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must unpledged something.'
    assert S[user, 'xoptic_pledge'
        ] >= amount, 'Not enough coins to unpledged!'
    con_xoptic_lst001.transfer_from(amount, user, metadata['operator'])
    metadata['xoptic_pledge'] -= amount
    metadata['xoptic_staked'] += amount
    S[user, 'xoptic_pledge'] -= amount
    metadata['total_lens'] -= S[user, 'lens']
    S[user, 'lens'] = 0
    S[user, 'start_lens'] = None
    if S[user, 'xoptic_pledge'] > 0:
        S[user, 'lens_time'] = now
        S[user, 'start_lens'] = now


@export
def active_lens():
    block_emergency()
    user = ctx.caller
    MAX_LENS = 0
    assert S[user, 'xoptic_pledge'] > 0, 'Not optics to lens'
    lens = S[user, 'xoptic_pledge'] * (metadata['lens_factor'] / (60 * 60)
        ) * (now - S[user, 'lens_time']).seconds


    
    if S[user, 'nft_active'] or S[user, 'nft_active'] is not None:
            thing_info = I.import_module(metadata['nft_contract'])
            uid = S[user, 'nft_active']
            active = thing_info.get_boost_owner(user, uid)
            MAX_LENS = 100 * active

    if lens + S[user, 'lens'] >= S[user, 'xoptic_pledge'] * (metadata
        ['max_lens'] + MAX_LENS):
        metadata['total_lens'] += lens + S[user, 'lens'] - S[user,
            'xoptic_pledge'] * (metadata['max_lens'] + MAX_LENS)
        S[user, 'lens'] = S[user, 'xoptic_pledge'] * (metadata[
            'max_lens'] + MAX_LENS)
        S[user, 'lens_time'] = now
    else:
        S[user, 'lens_time'] = now
        S[user, 'lens'] += lens
        metadata['total_lens'] += lens
    return MAX_LENS


@export
def register_external_link(wallet: str, dapp: str):
    block_emergency()
    user = ctx.caller

    assert L[dapp, wallet, 'owner'] != wallet, 'Dapps link its ready'

    L[dapp, wallet] = ['ref', 'owner']
    L[dapp, wallet, 'ref'] = user
    L[dapp, wallet, 'owner'] = wallet


@export
def active_dapps_link(dapp: str):
    block_emergency()
    user = ctx.caller
    if L[dapp, user] is not None:
        LINK[L[dapp, user, 'ref'], dapp, 'ACTIVE'] = user


@export
def remove_dapps_link(dapp: str):
    block_emergency() 
    user = ctx.caller
    if L[dapp, user] is not None:
        L[dapp, user] = None
        L[dapp, user, 'ref'] = None
        L[dapp, user, 'owner'] = None


def block_emergency():
    assert blockdata['block_emergency'] == False, 'Block funcion!'


@export
def claim():
    block_emergency()
    user = ctx.caller
    assert S[user, 'claimable'] > 0, 'Not optics to claim'
    FEES = S[user, 'claimable'] * metadata['rewards_fees']
    con_optic_lst001.transfer_from(S[user, 'claimable'] - FEES, user,
        metadata['operator'])
    con_optic_lst001.transfer_from(FEES, metadata['fees_wallet'],
        metadata['operator'])
    S[user, 'claimable'] = 0
    metadata['fees'] += FEES



@export
def claim_pledge():
    block_emergency()
    assert blockdata['xoptic_start'] == True, 'Deposit not start'
    user = ctx.caller
    assert S[user, 'claimable'] > 0, 'You must stake something.'

    FEES = S[user, 'claimable'] * metadata['rewards_fees']
    amount = S[user, 'claimable'] - FEES
    metadata['fees'] += FEES

    con_optic_lst001.transfer_from(FEES, metadata['fees_wallet'], metadata['operator'])
    S[user, 'claimable'] = 0
    
    #stake
    X_SUPPLY = metadata['xoptic_supply']
    OPTIC_IN_POOL = metadata['optic_in_pool']
    RECEIVED = amount / (OPTIC_IN_POOL + amount) * X_SUPPLY
    
    #con_optic_lst001.transfer_from(amount, metadata['operator'], user)
    #con_xoptic_lst001.transfer_from(RECEIVED, user, metadata['operator'])
    
    metadata['optic_in_pool'] += amount
    metadata['xoptic_supply'] -= RECEIVED
    metadata['xoptic_ratio'] = metadata['optic_in_pool'] / metadata[
        'xoptic_supply']
    metadata['optic_staked'] += amount
    metadata['xoptic_staked'] += RECEIVED
    S[user, 'xoptic'] += RECEIVED
     
    amount = RECEIVED
    #pledge
    MAX_LENS = 0
    metadata['xoptic_pledge'] += amount
    metadata['xoptic_staked'] -= amount
    S[user, 'xoptic_pledge'] += amount

    if not S[user, 'start_lens'] or S[user, 'start_lens'] is None:
        S[user, 'start_lens'] = now

    if S[user, 'lens'] == 0 or S[user, 'lens'] is None:
        S[user, 'lens'] = 0
        S[user, 'lens_time'] = now

    else:

        if S[user, 'nft_active'] or S[user, 'nft_active'] is not None:
            thing_info = I.import_module(metadata['nft_contract'])
            uid = S[user, 'nft_active']
            active = thing_info.get_boost_owner(user, uid)
            MAX_LENS = 100 * active
     

        lens = S[user, 'xoptic_pledge'] * (metadata['lens_factor'] / (
            60 * 60)) * (now - S[user, 'lens_time']).seconds
        if lens + S[user, 'lens'] >= S[user, 'xoptic_pledge'] * (metadata
            ['max_lens'] + MAX_LENS):
            metadata['total_lens'] += lens + S[user, 'lens'] - S[user,
                'xoptic_pledge'] * (metadata['max_lens'] + MAX_LENS)
            S[user, 'lens'] = S[user, 'xoptic_pledge'] * (metadata[
                'max_lens'] + MAX_LENS)
            S[user, 'lens_time'] = now
        else:
            S[user, 'lens'] += lens
            metadata['total_lens'] += lens
            S[user, 'lens_time'] = now

@export
def add_rewards(to: str, amount_base: float, amount_boost: float, uid: str):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'

    S[to, 'claimable'] += amount_base + amount_boost

@export
def active_nft(uid: str):
     user = ctx.caller
     thing_info = I.import_module(metadata['nft_contract'])
     assert_ownership(uid, user)
     S[user, 'nft_active'] = uid

@export
def sell_nft(uid: str, amount: float):
    thing_info = I.import_module(metadata['nft_contract'])
    assert_ownership(uid, ctx.caller)
    thing_info.set_price(uid, amount)

@export
def buy_nft(uid: str):
    thing_info = I.import_module(metadata['nft_contract'])
    sender = ctx.caller
    owner = thing_info.get_owner(uid)
    assert_already_owned(uid, sender)
    price_amount = thing_info.get_price(uid)

    assert price_amount, uid + ' is not for sale'
    assert price_amount > 0, uid + ' is not for sale'

    con_optic_lst001.transfer_from(price_amount, owner, sender)
   
    S[owner, 'nft_active'] = None

    transfer_ownership(uid, sender)

@export
def set_owner_nft(uid: str, to:str):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    thing_info = I.import_module(metadata['nft_contract'])
    owner = thing_info.get_owner(uid)   
    S[owner, 'nft_active'] = None
    transfer_ownership(uid, to)

def assert_already_owned(uid: str, sender: str):
    thing_info = I.import_module(metadata['nft_contract'])
    owner = thing_info.get_owner(uid)
    assert owner != sender, uid + ' already owned by ' + sender

def assert_ownership(uid: str, sender: str):
    thing_info = I.import_module(metadata['nft_contract'])
    owner = thing_info.get_owner(uid)
    assert owner == sender, uid + ' not owned by ' + sender

def transfer_ownership(uid:str, new_owner: str):
    thing_info = I.import_module(metadata['nft_contract'])
    thing_info.set_owner(uid, new_owner)
    if thing_info.get_price(uid) > 0:
        thing_info.set_price(uid, 0)


@export
def burn(amount: float):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    metadata['burn'] -= amount


@export
def fees(amount: float):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    metadata['fees'] -= amount


@export
def buyback(amount: float):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    metadata['buyback'] += amount
    metadata['optic_in_pool'] += amount
    metadata['xoptic_ratio'] = metadata['optic_in_pool'] / metadata[
        'xoptic_supply']

@export
def import_emergency_user(to: str, data: dict):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    
    assert metadata['emergency_contract'] == 1 , 'Not use'
    for d in data:
        S[to, d] = data[d]


@export
def import_emergency_contract(data: dict):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    
    assert metadata['emergency_contract'] == 1 , 'Not use'
   
    for d in data:
        metadata[d] = data[d]

    metadata['emergency_contract'] = 0

@export
def change_blockdata(key: str, value: Any):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    blockdata[key] = value


@export
def change_meta(key: str, value: Any):
    assert_signer_is_operator()

    metadata[key, ctx.caller] = value

    agreed = True

    for op in metadata['operator_sign']:
        if metadata[key, op] != metadata[key, ctx.caller]:
            agreed = False
            break

    if agreed:
        metadata[key] = value

        for op in metadata['operator_sign']:
            metadata[key, op] = hashlib.sha256(str(now))

@export
def remove_tau_emergency(amount: float):
    assert_signer_is_operator()

    metadata['remove_tau_emergency', ctx.caller] = amount
    agreed = True

    for op in metadata['operator_sign']:
        if metadata['remove_tau_emergency', op] != metadata['remove_tau_emergency', ctx.caller]:
            agreed = False
            break

    if agreed:
        currency.transfer_from(amount, metadata['operator'], ctx.this)

        for op in metadata['operator_sign']:
            metadata['remove_tau_emergency', op] = 0

@export
def assert_signer_is_operator():
    assert ctx.signer in metadata['operator_sign'], 'Only executable by operators!'
