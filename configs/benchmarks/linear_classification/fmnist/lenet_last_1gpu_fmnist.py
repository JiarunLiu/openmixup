_base_ = '../../../base.py'
# model settings
model = dict(
    type='Classification',
    backbone=dict(  # mmclassification
        type='LeNet5',
        activation="LeakyReLU",
        mlp_neck=None,
        cls_neck=True,
    ),
    head=dict(
        type='ClsHead', with_avg_pool=False, in_channels=84,
        num_classes=10))
# dataset settings
data_source_cfg = dict(type='Fmnist', root='./data/')
dataset_type = 'ClassificationDataset'
img_norm_cfg = dict(mean=[0.], std=[1.])  # MNIST grayscale
resizeto = 32
test_pipeline = [
    dict(type='Resize', size=resizeto),
    dict(type='ToTensor'),
    dict(type='Normalize', **img_norm_cfg),
]
data = dict(
    imgs_per_gpu=100,
    workers_per_gpu=2,
    val=dict(
        type=dataset_type,
        data_source=dict(split='test', **data_source_cfg),
        pipeline=test_pipeline),
)
# additional hooks
custom_hooks = [
    dict(
        type='ValidateHook',
        dataset=data['val'],
        initial=True,
        interval=10,
        imgs_per_gpu=128,
        workers_per_gpu=2,
        eval_param=dict(topk=(1, 5)))
]
# optimizer
optimizer = dict(type='SGD', lr=0.1, momentum=0.9, weight_decay=0.)
# learning policy
lr_config = dict(policy='step', step=[60, 80])
checkpoint_config = dict(interval=50)
# runtime settings
total_epochs = 100
