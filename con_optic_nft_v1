
metadata = Hash(default_value=0)


@construct
def seed():
    metadata['operator'] = ctx.caller
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
    metadata['master_contract'].add(key)

@export
def mint(thing: str, name: str, meta: dict, creator: str, stage: int):
    is_operator()
    uid = hashlib.sha256(thing)
    assert not S[uid], thing + ' already exists'
    S[uid] = ['thing', 'type', 'name', 'owner', 'creator', 'stage', 'price:amount',
        'meta_items']
    S[uid, 'thing'] = thing
    S[uid, 'type'] = 'text/plain'
    S[uid, 'name'] = name
    S[uid, 'owner'] = creator
    S[uid, 'stage'] = stage
    S[uid, 'creator'] = creator
    S[uid, 'price', 'amount'] = 0
    S[uid, 'meta_items'] = ['boost']
    S[uid, 'meta', 'boost'] = meta['boost']
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

def is_operator(caller: str):
    assert ctx.signer == metadata['operator'], 'Only executable by operators!'

def is_contract_operator(caller: str):
    assert caller in metadata['master_contract'], 'Only executable by operator contracts!'
