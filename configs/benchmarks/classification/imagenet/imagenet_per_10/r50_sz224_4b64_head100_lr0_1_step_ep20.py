_base_ = [
    'r50_sz224_4b64_head1_lr0_1_step_ep20.py',
]

# optimizer
optimizer = dict(paramwise_options={'\\Ahead.': dict(lr_mult=100)})
