
import con_optic_lst001

metadata = Hash(default_value=0)
S = Hash(default_value=0)

@construct
def seed():
    metadata['operator'] = ctx.caller
    metadata['fees'] = decimal('0.1')
    metadata['fees_wallet'] = 'eb9074ab07c502be35be4f447d370a79ac9feb62e849fe0272dfe93d0e4cdd48'
    metadata['master_contract'] = [
        'con_optic_protocol',
        'con_optic_protocol_marketplace'
    ]

@export
def change_metadata(key: str, value: Any):
    is_operator()
    metadata[key] = value

@export
def add_master_contract(key: str):
    is_operator()
    metadata['master_contract'].append(key)

@export
def mint(url: str, name: str, meta: dict, creator: str, stage: int):
    is_operator()
    uid = hashlib.sha256(thing)
    assert not S[uid], thing + ' already exists'
    S[uid] = ['url', 'type', 'name', 'owner', 'creator', 'stage', 'price:amount','meta_items']
    S[uid, 'url'] = url
    S[uid, 'type'] = 'text/plain'
    S[uid, 'name'] = name
    S[uid, 'owner'] = creator
    S[uid, 'stage'] = stage
    S[uid, 'creator'] = creator
    S[uid, 'price', 'amount'] = 0
    S[uid, 'meta_items'] = ['boost','type_boost']
    S[uid, 'meta', 'boost'] = meta['boost']
    S[uid, 'meta', 'type_boost'] = meta['type_boost']
    return uid


@export
def exists(thing: str):
    uid = hashlib.sha256(thing)
    return S[uid]

@export
def get_owner(uid: str):
    return S[uid, 'owner']

@export
def get_boost(uid: str):
    return S[uid, 'meta', 'boost']

@export
def get_boost_type(owner: str, uid: str):
    own = get_owner(uid)
    if own == owner:
        return S[uid, 'meta', 'type_boost']
    else:
        return False

@export
def get_boost_owner(owner: str, uid: str):
    own = get_owner(uid)
    if own == owner:
        return S[uid, 'meta', 'boost']
    else:
        return 0

@export
def get_price(uid: str):
    return S[uid, 'price', 'amount']

@export
def set_price(uid: str, amount: float):
    is_contract_operator(ctx.caller)
    assert amount >= 0, 'Cannot set a negative price'
    S[uid, 'price', 'amount'] = amount


@export
def set_owner(uid: str, owner: str):
    is_contract_operator(ctx.caller)
    S[uid, 'owner'] = owner

@export
def active_nft(uid: str):
    sender = ctx.caller
    assert_ownership(uid, sender)
    S[sender, 'nft_active'] = uid

@export
def sell_nft(uid: str, amount: float):
    sender = ctx.caller
    assert_ownership(uid, sender)
    S[uid, 'price', 'amount'] = amount

@export
def buy_nft(uid: str):
    sender = ctx.caller
    owner = get_owner(uid)
    assert_already_owned(uid, sender)
    price_amount = get_price(uid)

    assert price_amount, uid + ' is not for sale'
    assert price_amount > 0, uid + ' is not for sale'
   
    FEES = price_amount * metadata['fees']
    con_optic_lst001.transfer_from(price_amount - FEES, owner, sender)
    con_optic_lst001.transfer_from(FEES, metadata['fees_wallet'], sender)
    
    S[owner, 'nft_active'] = None
    S[uid, 'owner'] = sender
    S[uid, 'price', 'amount'] = 0

@export
def transfer_nft(uid: str, to: str):
    sender = ctx.caller
    owner = get_owner(uid)
    assert_ownership(uid, sender)

    S[owner, 'nft_active'] = None

    S[uid, 'owner'] = to
    S[uid, 'price', 'amount'] = 0


def assert_already_owned(uid: str, sender: str):
    owner = get_owner(uid)
    assert owner != sender, uid + ' already owned by ' + sender

def assert_ownership(uid: str, sender: str):
    owner = get_owner(uid)
    assert owner == sender, uid + ' not owned by ' + sender

def is_operator(caller: str):
    assert ctx.signer == metadata['operator'], 'Only executable by operators!'

def is_contract_operator(caller: str):
    assert caller in metadata['master_contract'], 'Only executable by operator contracts!'
