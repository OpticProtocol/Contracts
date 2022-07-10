import con_rswp_lst001
import con_optic_srswp_lst001
I = importlib


S = Hash(default_value=0)

metadata = Hash(default_value=0)
blockdata = Hash(default_value=0)


RSWP = ForeignHash(foreign_contract='con_rswp_lst001', foreign_name='balances')
sRSWP = ForeignHash(foreign_contract='con_optic_srswp_lst001', foreign_name='balances')

@construct
def seed():
    metadata['operator'] = ctx.caller
    metadata['fees_wallet'] = 'eb9074ab07c502be35be4f447d370a79ac9feb62e849fe0272dfe93d0e4cdd48'
    metadata['boost_pool'] = 40_000_000
    metadata['srswp_convert'] = 0
    metadata['srswp_farm'] = 0
    metadata['contract_farm'] = 0

    blockdata['farm_end'] = False
    metadata['rewards_fees'] = decimal('0.1')   
    blockdata['block_emergency'] = False  
    metadata['instant_burn'] = decimal('0.03')
    metadata['rswp_contract'] = 'con_staking_rswp_rswp_interop_v2' 
    metadata['var_contract'] = 'Deposits'
    metadata['operator_sign'] = [ctx.caller, '24f4184c9d9e8e8440067e75fb4c82d44c51c529581dd40e486a0ca989639600', 'b1c4b6a0baa3cef7fd57a191d3fe0798748b439ddf566825a2b614eb250bb519']

    con_rswp_lst001.approve(999_999_999_999_999_999, ctx.this)
    con_rswp_lst001.approve(999_999_999_999_999_999, metadata['rswp_contract'])
    con_optic_srswp_lst001.approve(999_999_999_999_999_999, ctx.this)


@export
def convert(amount: float):
    #convert rswp token to srswp token
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must stake something.'
    assert RSWP[user] >= amount, 'Not enough coins to send!'
    
    con_rswp_lst001.transfer_from(amount, ctx.this, user)
    con_optic_srswp_lst001.transfer_from(amount, user, ctx.this)

    metadata['srswp_convert'] += amount
    return amount


@export
def redeem_instant(amount: float):
    #redeem instant rswp token
    #pay fee in rswp (0.03)
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must stake something.'
    assert sRSWP[user] >= amount, 'Not enough sRSWP to send!'
    
    con_optic_srswp_lst001.transfer_from(amount, ctx.this, user)
    BURN = amount * metadata['instant_burn']
    metadata['fees'] += BURN
    if blockdata['farm_end'] == False:

        #remove all farm in rocketswap
        ROCKET = I.import_module(metadata['rswp_contract'])

        REMOVE = ROCKET.withdrawYield(amount=999_999_999)

        ROCKET.withdrawTokensAndYield()
        #calculate initial balance and Yield amount
        REWARDS = REMOVE

        metadata['contract_farm'] += REWARDS

        con_rswp_lst001.transfer_from(amount - BURN, user, ctx.this)    
        con_rswp_lst001.transfer_from(BURN, metadata['fees_wallet'], ctx.this)

        #calculate balance amount
        TOTAL = RSWP[ctx.this]  
        #add staking in rocketswap again
        ROCKET.addStakingTokens(amount=TOTAL)
        
    else:
        con_rswp_lst001.transfer_from(amount - BURN, user, ctx.this)    
        con_rswp_lst001.transfer_from(BURN, metadata['fees_wallet'], ctx.this)
    
    metadata['srswp_convert'] -= amount
    return amount


@export
def redeem_slow(amount: float):
    #redeem rswp, no pay fee
    #the unstaking period which is 7 days.
    block_emergency() 
    user = ctx.caller
    assert amount > 0, 'You must stake something.'
    assert sRSWP[user] >= amount, 'Not enough sRSWP to send!'

    con_optic_srswp_lst001.transfer_from(amount, ctx.this, user)

    metadata['srswp_convert'] -= amount
    return amount


@export
def claim_merge_slow():
    block_emergency()
    user = ctx.caller
    amount = S[user, 'merge']
    assert amount > 0, 'You must claim something.'
    
    if blockdata['farm_end'] == False:

        #remove all farm in rocketswap
        ROCKET = I.import_module(metadata['rswp_contract'])

        REMOVE = ROCKET.withdrawYield(amount=999_999_999)
        
        ROCKET.withdrawTokensAndYield()

        #calculate initial balance and Yield amount
        REWARDS = REMOVE
        metadata['contract_farm'] += REWARDS

        con_rswp_lst001.transfer_from(amount, user, ctx.this)

        #calculate balance amount
        TOTAL = RSWP[ctx.this]
        #add staking in rocketswap again
        ROCKET.addStakingTokens(amount=TOTAL)
    else:
        con_rswp_lst001.transfer_from(amount, user, ctx.this)        

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

    assert amount > 0, 'You must stake something.'
    assert sRSWP[user] >= amount, 'Not enough coins to stake!'
   
    con_optic_srswp_lst001.transfer_from(amount, ctx.this, user)

    if blockdata['farm_end'] == False:
        #only if user farm with srswp
        #add the amount in staking in rocketswap
        ROCKET = I.import_module(metadata['rswp_contract'])
        ROCKET.addStakingTokens(amount=amount)

    if S[user, 'start_farm'] is None:
        S[user, 'start_farm'] = now
        
    metadata['srswp_farm'] += amount
    S[user, 'farm'] += amount
    return S[user, 'start_farm']


@export
def remove(amount: float):
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must withdrawal something.'
    assert S[user, 'farm'] >= amount, 'Not enough coins to withdrawal!'
    con_optic_srswp_lst001.transfer_from(amount, user, ctx.this)

    metadata['srswp_farm'] -= amount
    S[user, 'farm'] -= amount
    if S[user, 'farm'] == 0:
        S[user, 'start_farm'] = None

def block_emergency():
    assert blockdata['block_emergency'] == False, 'Block funcion!'

@export
def claim():
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
def add_rewards(to: str, amount:float, uid: str):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'

    S[to, 'claimable'] += amount


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
def remove_all_farm():
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'

    #claim rewards in rocketswap
    ROCKET = I.import_module(metadata['rswp_contract'])
    ROCKET.withdrawTokensAndYield()

@export
def claim_contract_rewards():
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'

    #claim rewards in rocketswap
    ROCKET = I.import_module(metadata['rswp_contract'])
    metadata['contract_farm'] += ROCKET.withdrawYield(amount=999_999_999)
    return metadata['contract_farm']

@export
def remove_claim_rewards(amount: float):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'

    assert amount <= metadata['contract_farm'] , 'Only remove rewards'

    con_rswp_lst001.transfer_from(amount, metadata['operator'], ctx.this)


@export
def remove_emergency(amount: float):
    #remove amount of rswp token for emergency
    #multising method
    assert_signer_is_operator()
    metadata['remove', ctx.caller] = amount
    agreed = True

    for op in metadata['operator_sign']:
        if metadata['remove', op] != metadata['remove', ctx.caller]:
            agreed = False
            break

    if agreed:
        con_rswp_lst001.transfer_from(amount, metadata['operator'], ctx.this)

        for op in metadata['operator_sign']:
            metadata['remove', op] = 0

@export
def remove_srswp_emergency(amount: float):
    #remove amount of rswp token for emergency
    #multising method
    assert_signer_is_operator()
    metadata['remove_srswp', ctx.caller] = amount
    agreed = True

    for op in metadata['operator_sign']:
        if metadata['remove_srswp', op] != metadata['remove_srswp', ctx.caller]:
            agreed = False
            break

    if agreed:
        con_optic_srswp_lst001.transfer_from(amount, metadata['operator'], ctx.this)

        for op in metadata['operator_sign']:
            metadata['remove_srswp', op] = 0

def block_emergency():
    assert metadata['block_emergency'] == False, 'Block funcion!'            
            
@export
def assert_signer_is_operator():
    assert ctx.signer in metadata['operator_sign'], 'Only executable by operators!'
