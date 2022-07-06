import currency
import con_optic_lst001
import con_rswp_lst001
import con_optic_srwsp_lst001
I = importlib


S = Hash(default_value=0)

metadata = Hash(default_value=0)
blockdata = Hash(default_value=0)


TAU = ForeignHash(foreign_contract='currency', foreign_name='balances')
OPTIC = ForeignHash(foreign_contract='con_optic_lst001', foreign_name='balances')
RWSP = ForeignHash(foreign_contract='con_rswp_lst001', foreign_name='balances')
sRWSP = ForeignHash(foreign_contract='con_optic_srwsp_lst001', foreign_name='balances')

@construct
def seed():
    metadata['operator'] = ctx.caller
    metadata['fees_wallet'] = 'eb9074ab07c502be35be4f447d370a79ac9feb62e849fe0272dfe93d0e4cdd48'
    metadata['boost_pool'] = 30_000_000
    metadata['srwsp_convert'] = 0
    metadata['srwsp_farm'] = 0
    metadata['contract_farm'] = 0
    metadata['rewards_fees'] = decimal('0.1')   
    blockdata['block_emergency'] = False  
    metadata['instant_burn'] = decimal('0.03')
    metadata['rwsp_contract'] = 'con_staking_rswp_rswp_interop_v2' 
    metadata['var_contract'] = 'Deposits'
    metadata['operator_sign'] = [ctx.caller, '24f4184c9d9e8e8440067e75fb4c82d44c51c529581dd40e486a0ca989639600', 'b1c4b6a0baa3cef7fd57a191d3fe0798748b439ddf566825a2b614eb250bb519']

    con_rswp_lst001.approve(999_999_999_999_999_999, ctx.this)
    con_optic_srwsp_lst001.approve(999_999_999_999_999_999, ctx.this)


@export
def convert(amount: float):
    #convert rwsp token to srwsp token
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must stake something.'
    assert RWSP[user] >= amount, 'Not enough coins to send!'
    
    con_rswp_lst001.transfer_from(amount, ctx.this, user)
    con_optic_srwsp_lst001.transfer_from(amount, user, ctx.this)

    metadata['srwsp_convert'] += amount
    return amount


@export
def redeem_instant(amount: float):
    #redeem instant rwsp token
    #pay fee in rwsp (0.03)
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must stake something.'
    assert sRWSP[user] >= amount, 'Not enough sRWSP to send!'
    
    con_optic_srwsp_lst001.transfer_from(amount, ctx.this, user)
    BURN = amount * metadata['instant_burn']
    
    #calculate balance amount
    rswp_balance = ForeignHash(foreign_contract=metadata['rwsp_contract'], foreign_name=metadata['var_contract'])
    TOTAL = rswp_balance[ctx.this]['amount']   
    
    #remove all farm in rocketswap
    ROCKET = I.import_module(metadata['rwsp_contract'])
    REMOVE = ROCKET.withdrawTokensAndYield()
    
    #calculate initial balance and Yield amount
    REWARDS = REMOVE - TOTAL
    
    metadata['fees'] += BURN
    metadata['contract_farm'] += REWARDS

    con_rswp_lst001.transfer_from(amount - BURN, user, ctx.this)    
    con_rswp_lst001.transfer_from(BURN, metadata['fees_wallet'], ctx.this)
    
    #calculate balance amount
    TOTAL = rswp_balance[ctx.this]['amount']  
    #add staking in rocketswap again
    ROCKET.addStakingTokens(amount=TOTAL)
    
    metadata['srwsp_convert'] -= amount
    return amount


@export
def redeem_slow(amount: float):
    #redeem rswp, no pay fee
    #the unstaking period which is 7 days.
    block_emergency() 
    user = ctx.caller
    assert amount > 0, 'You must stake something.'
    assert sRWSP[user] >= amount, 'Not enough sRWSP to send!'

    con_optic_srwsp_lst001.transfer_from(amount, ctx.this, user)

    metadata['srwsp_convert'] -= amount
    return amount


@export
def claim_merge_slow():
    block_emergency()
    user = ctx.caller
    amount = S[user, 'merge']
    assert amount > 0, 'You must claim something.'
    
    #calculate balance amount
    rswp_balance = ForeignHash(foreign_contract=metadata['rwsp_contract'], foreign_name=metadata['var_contract'])
    TOTAL = rswp_balance[ctx.this]['amount']  
    
    #remove all farm in rocketswap
    ROCKET = I.import_module(metadata['rwsp_contract'])
    REMOVE = ROCKET.withdrawTokensAndYield()
    
    #calculate initial balance and Yield amount
    REWARDS = REMOVE - TOTAL
    metadata['contract_farm'] += REWARDS
    
    con_rswp_lst001.transfer_from(amount, user, ctx.this)
    
    #calculate balance amount
    TOTAL = rswp_balance[ctx.this]['amount']  
    #add staking in rocketswap again
    ROCKET.addStakingTokens(amount=TOTAL)

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
    assert sRWSP[user] >= amount, 'Not enough coins to stake!'
   
    con_optic_srwsp_lst001.transfer_from(amount, ctx.this, user)

    #only if user farm with srwsp
    #add the amount in staking in rocketswap
    ROCKET = I.import_module(metadata['rwsp_contract'])
    ROCKET.addStakingTokens(amount=amount)

    if S[user, 'start_farm'] is None:
        S[user, 'start_farm'] = now
        
    metadata['srwsp_farm'] += amount
    S[user, 'farm'] += amount
    return S[user, 'start_farm']


@export
def remove(amount: float):
    block_emergency()
    user = ctx.caller
    assert amount > 0, 'You must withdrawal something.'
    assert S[user, 'farm'] >= amount, 'Not enough coins to withdrawal!'
    con_optic_srwsp_lst001.transfer_from(amount, user, ctx.this)

    metadata['srwsp_farm'] -= amount
    S[user, 'farm'] -= amount
    if S[user, 'farm'] == 0:
        S[user, 'start_farm'] = None

def block_emergency():
    assert blockdata['block_emergency'] == False, 'Block funcion!'


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
def claim_contract_farm():
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'

    #claim rewards in rocketswap
    ROCKET = I.import_module(metadata['rwsp_contract'])
    metadata['contract_farm'] += ROCKET.withdrawYield(amount=999_999_999)
    return metadata['contract_farm']

@export
def remove_emergency(amount: float):
    #remove amount of rwsp token for emergency
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

def block_emergency():
    assert metadata['block_emergency'] == False, 'Block funcion!'            
            
@export
def assert_signer_is_operator():
    assert ctx.signer in metadata['operator_sign'], 'Only executable by operators!'
