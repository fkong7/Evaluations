# evaluate all experiements in a folder
#experiment_dir=/Users/fanweikong/Documents/Modeling/HeartDeepFFD/output/2021-10-8
gt_pattern="/Users/fanweikong/Documents/ImageData/multidataset_whole_heart/ct_val_seg/"
experiment_dir=/Users/fanweikong/Documents/Modeling/HeartDeepFFD/output/2022-01-01
experiment_dir=/Users/fanweikong/Documents/Modeling/HeartDeepFFD/output/2022-02-25
#experiment_dir=/Users/fanweikong/Documents/Modeling/HeartDeepFFD/results/Geometric_Accuracy/Multi
#experiment_dir=/Users/fanweikong/Documents/Modeling/HeartDeepFFD/output/2021-12-04
gt_pattern=/Users/fanweikong/Documents/ImageData/MMWHS/test_gt_masks

for dir in $experiment_dir/*mmwhs_template1_gapfix_wt05n05n05*
do
    echo $dir
    for sub_dir in $dir/*
    do
        echo $sub_dir
        python evaluation.py --gt_pattern "$gt_pattern/*.nii.gz" --pred_pattern "$sub_dir/*.nii.gz" --output_name ct_
        python evaluation.py --gt_pattern "$gt_pattern/mr*.nii.gz" --pred_pattern "$sub_dir/mr*.nii.gz" --output_name mr_
    done
done

#experiment_dir=/Users/fanweikong/Documents/Modeling/HeartDeepFFD/results/Geometric_Accuracy/MultiFull
#experiment_dir=/Users/fanweikong/Documents/Modeling/HeartDeepFFD/output/2022-01-01
#gt_pattern=/Users/fanweikong/Documents/ImageData/4DCCTA/gt_full_masks
#for dir in $experiment_dir/cap_param20_03n046_1500_capOnly_dataWt1n10n05_wt1n05n05
#do
#    echo $dir
#    python evaluation.py --gt_pattern "$gt_pattern/*.nii*" --pred_pattern "$dir/4DCT_gt/*.nii*" --output_name ct_
#    python evaluation.py --gt_pattern "$gt_pattern/*.nii*" --pred_pattern "$dir/4DCT_gt_sample/*.nii*" --output_name ct_
#done
#for dir in $experiment_dir/*
#do
#    echo $dir
#    python evaluation.py --gt_pattern "$gt_pattern/*.nii*" --pred_pattern "$dir/4DCT_gt/*.nii*" --output_name ct_
#    python evaluation.py --gt_pattern "$gt_pattern/*.nii*" --pred_pattern "$dir/4DCT_gt_sample/*.nii*" --output_name ct_
#done






