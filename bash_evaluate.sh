# evaluate all experiements in a folder
experiment_dir=/Users/fanweikong/Documents/Modeling/HeartDeepFFD/output/2021-10-8
gt_pattern="/Users/fanweikong/Documents/ImageData/multidataset_whole_heart/ct_val_seg_full/*.nii.gz"

for dir in $experiment_dir/*
do
    echo $dir
    python evaluation.py --gt_pattern $gt_pattern --pred_pattern "$dir/val/*.nii.gz" --output_name ct
    python evaluation.py --gt_pattern $gt_pattern --pred_pattern "$dir/val_sample/*.nii.gz" --output_name ct
done
    






