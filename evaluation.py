import os
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import SimpleITK as sitk
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "vtk_utils"))
from vtk_utils import *
import csv
from metrics import *
import argparse
import glob

def natural_sort(l):
    import re
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

def write_scores(csv_path,scores, header=('Dice', 'ASSD')): 
    with open(csv_path, 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(header)
        for i in range(len(scores)):
            writer.writerow(tuple(scores[i]))
            print(scores[i])
    writeFile.close()

def convert_to_surfs(fn):
    seg = sitk.ReadImage(fn)
    py_seg = sitk.GetArrayFromImage(seg)
    py_seg = eraseBoundary(py_seg, 1, 0)
    labels = np.unique(py_seg)
    for i, l in enumerate(labels):
        py_seg[py_seg==l] = i
    seg2 = sitk.GetImageFromArray(py_seg)
    seg2.SetOrigin(seg.GetOrigin())
    seg2.SetSpacing(seg.GetSpacing())
    seg2.SetDirection(seg.GetDirection())
    seg_vtk,_ = exportSitk2VTK(seg2)
    new_spacing = [1.5,1.5,1.5]
    seg_vtk = vtkImageResample(seg_vtk,new_spacing,'NN')
    poly_l = []
    for i, _ in enumerate(labels):
        if i==0:
            continue
        p = vtk_marching_cube(seg_vtk, 0, i)
        poly_l.append(p)
    poly = appendPolyData(poly_l)
    ids = poly.GetCellData().GetArray(0)
    ids.SetName('Scalars_')
    poly.GetCellData().AddArray(ids)
    return poly

def evaluate_surfaces(pred_pat, gt_pat, out_name, num_region=7):
    pred_fns = natural_sort(glob.glob(pred_pat))
    pred_dir = os.path.dirname(pred_pat)
    gt_fns = natural_sort(glob.glob(gt_pat))
    assert len(pred_fns) == len(gt_fns), 'Unequal number of files between prediction and ground truth!'

    assd_list, haus_list = [], []
    for pred_fn, gt_fn in zip(pred_fns, gt_fns):
        try:
            pred_poly = load_vtk_mesh(pred_fn)
            gt_poly = load_vtk_mesh(gt_fn)
        except:
            pred_poly = convert_to_surfs(pred_fn)
            gt_poly = convert_to_surfs(gt_fn)
            #write_vtk_polydata(pred_poly, '/Users/fanweikong/Downloads/debug.vtp')
        assd, haus, poly_dist = evaluate_poly_distances(pred_poly, gt_poly, num_region)
        assd_list.append(assd)
        haus_list.append(haus)
        #write_vtk_polydata(poly_dist, os.path.join(pred_dir, 'dist_'+out_name+os.path.basename(pred_fn)))

    assd_path = os.path.join(pred_dir, out_name+'_assd.csv')
    haus_path = os.path.join(pred_dir, out_name+'_haus.csv')

    write_scores(assd_path, assd_list)
    write_scores(haus_path, haus_list)

def evaluate_segmentations(pred_pat, gt_pat, out_name):
    pred_fns = natural_sort(glob.glob(pred_pat))
    pred_dir = os.path.dirname(pred_pat)
    gt_fns = natural_sort(glob.glob(gt_pat))
    print("pred, gt: ", len(pred_fns), len(gt_fns))
    assert len(pred_fns) == len(gt_fns), 'Unequal number of files between prediction and ground truth!'
    dice_list, jaccard_list = [], []
    for pred_fn, gt_fn in zip(pred_fns, gt_fns):
        print(pred_fn, gt_fn)
        pred_im = sitk.ReadImage(pred_fn)
        pred_im_vtk, _ = exportSitk2VTK(pred_im)
        gt_im = sitk.ReadImage(gt_fn)
        gt_im_vtk, _ = exportSitk2VTK(gt_im)
        dice, jac = evaluate_segmentation_accuracy(pred_im_vtk, gt_im_vtk)
        dice_list.append(dice)
        jaccard_list.append(jac)
    dice_path = os.path.join(pred_dir, out_name+'test.csv')
    jac_path = os.path.join(pred_dir, out_name+'test_jaccard.csv')
    write_scores(dice_path, dice_list)
    write_scores(jac_path, jaccard_list)

if __name__ == '__main__':
    #gt_pat = 'examples/gt/mr_*.vtp'
    #pred_pat = 'examples/pred/block2_mr*.vtp'
    #out_name = 'mr_'
    parser = argparse.ArgumentParser()
    parser.add_argument('--gt_pattern', help='File pattern of ground truth files')
    parser.add_argument('--pred_pattern', help='File pattern of prediction files')
    parser.add_argument('--output_name', help='Output name, ct or mr')
    args = parser.parse_args()
    print("debug: ", args.pred_pattern)
    #evaluate_surfaces(args.pred_pattern, args.gt_pattern, args.output_name)
    evaluate_segmentations(args.pred_pattern, args.gt_pattern, args.output_name)

