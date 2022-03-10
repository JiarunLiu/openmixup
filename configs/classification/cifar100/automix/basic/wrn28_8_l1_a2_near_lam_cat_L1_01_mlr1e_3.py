_base_ = '../../../../base.py'

# model settings
model = dict(
    type='AutoMixup',
    pretrained=None,
    alpha=2.0,
    momentum=0.999,  # 0.999 to 0.999999
    mask_layer=1,  # for WRN
    mask_loss=0.1,  # using mask loss
    mask_adjust=0,
    lam_margin=0.08,  # degenerate to mixup when lam or 1-lam <= 0.08
    mask_up_override=None,  # If not none, override upsampling when train MixBlock
    debug=True,  # show attention and content map
    backbone=dict(
        type='WideResNet',
        first_stride=1,  # CIFAR version
        in_channels=3,
        depth=28, widen_factor=8,  # WRN-28-8, 128-256-512
        drop_rate=0.0,
        out_indices=(1,2,),  # no conv-1, stage-2 for MixBlock, x-1: stage-x
    ),
    mix_block = dict(  # AutoMix
        type='PixelMixBlock',
        in_channels=256, reduction=2, use_scale=True, double_norm=False,
        attention_mode='embedded_gaussian',
        unsampling_mode=['nearest',],  # str or list
        lam_concat=False, lam_concat_v=False,  # AutoMix.V1: no lam cat for small datasets
        lam_mul=False, lam_residual=False, lam_mul_k=-1,  # SAMix lam: none
        value_neck_cfg=None,  # SAMix: non-linear value
        x_qk_concat=False, x_v_concat=False,  # SAMix x concat: none
        att_norm_cfg=dict(type='BN'),  # AutoMix: attention norm (for fp16)
        mask_loss_mode="L1", mask_loss_margin=0.1,  # L1 loss, 0.1
        mask_mode="none_v_",
        frozen=False),
    head_one=dict(
        type='ClsHead',  # default CE
        loss=dict(type='CrossEntropyLoss', use_soft=False, use_sigmoid=False, loss_weight=1.0),
        with_avg_pool=True, multi_label=False, in_channels=512, num_classes=100),
    head_mix=dict(  # backbone & mixblock
        type='ClsMixupHead',  # mixup, default CE
        loss=dict(type='CrossEntropyLoss', use_soft=False, use_sigmoid=False, loss_weight=1.0),
        with_avg_pool=True, multi_label=False, in_channels=512, num_classes=100),
    head_weights=dict(
        head_mix_q=1, head_one_q=1, head_mix_k=1, head_one_k=1),
)
# dataset settings
data_source_cfg = dict(type='CIFAR100', root='data/cifar100/')
dataset_type = 'ClassificationDataset'
img_norm_cfg = dict(mean=[0.4914, 0.4822, 0.4465], std=[0.2023, 0.1994, 0.201])
train_pipeline = [
    dict(type='RandomCrop', size=32, padding=4, padding_mode="reflect"),
    dict(type='RandomHorizontalFlip'),
]
test_pipeline = []
# prefetch
prefetch = True
if not prefetch:
    train_pipeline.extend([dict(type='ToTensor'), dict(type='Normalize', **img_norm_cfg)])
test_pipeline.extend([dict(type='ToTensor'), dict(type='Normalize', **img_norm_cfg)])

data = dict(
    imgs_per_gpu=100,
    workers_per_gpu=4,
    train=dict(
        type=dataset_type,
        data_source=dict(split='train', **data_source_cfg),
        pipeline=train_pipeline,
        prefetch=prefetch,
    ),
    val=dict(
        type=dataset_type,
        data_source=dict(split='test', **data_source_cfg),
        pipeline=test_pipeline,
        prefetch=False),
)

# additional hooks
custom_hooks = [
    dict(type='ValidateHook',
        dataset=data['val'],
        initial=False,
        interval=1,
        imgs_per_gpu=100,
        workers_per_gpu=4,
        eval_param=dict(topk=(1, 5))),
    dict(type='CosineScheduleHook',
        end_momentum=0.999999,
        adjust_scope=[0.1, 1.0],
        warming_up="constant",
        interval=1),
    dict(type='SAVEHook',
        iter_per_epoch=500,
        save_interval=12500,  # plot every 500 x 25 ep
    )
]

# optimizer
optimizer = dict(type='SGD', lr=0.03, momentum=0.9, weight_decay=0.001,  # lr=3e-2 + wd=1e-3 for WRN
                paramwise_options={
                    'mix_block': dict(lr=0.03, momentum=0)})  # momentum=0 performs better in 400ep
optimizer_config = dict(grad_clip=None)

# learning policy
lr_config = dict(policy='CosineAnnealing', min_lr=1e-3)
checkpoint_config = dict(interval=800)

# runtime settings
total_epochs = 400
