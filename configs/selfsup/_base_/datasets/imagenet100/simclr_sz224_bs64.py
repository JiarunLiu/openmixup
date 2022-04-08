_base_ = '../imagenet/simclr_sz224_bs64.py'

# dataset settings
data_source_cfg = dict(type='ImageNet')
# ImageNet dataset, 100 class
data_train_list = 'data/meta/ImageNet100/train.txt'
data_train_root = 'data/ImageNet/train'

# dataset summary
data = dict(
    train=dict(
        data_source=dict(
            list_file=data_train_list, root=data_train_root,
            **data_source_cfg),
    ))