import os
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import SimpleITK as sitk
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from utils import *
import csv


def write_scores(csv_path,scores): 
    with open(csv_path, 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(('Dice', 'ASSD'))
        for i in range(len(scores)):
            writer.writerow(tuple(scores[i]))
            print(scores[i])
    writeFile.close()

def extract_surface(poly):
    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputData(poly)
    connectivity.ColorRegionsOn()
    connectivity.SetExtractionModeToAllRegions()
    connectivity.Update()
    poly = connectivity.GetOutput()
    return poly

def surface_distance(p_surf, g_surf):
    dist_fltr = vtk.vtkDistancePolyDataFilter()
    dist_fltr.SetInputData(1, p_surf)
    dist_fltr.SetInputData(0, g_surf)
    dist_fltr.SignedDistanceOff()
    dist_fltr.Update()
    distance = vtk_to_numpy(dist_fltr.GetOutput().GetPointData().GetArray('Distance'))
    return distance, dist_fltr.GetOutput()


def evaluate_poly(poly, gt, NUM):
    # compute assd and hausdorff distances
    assd_list, haus_list, poly_list = [], [], []
    poly =extract_surface(poly)
    for i in range(NUM):
        poly_i = thresholdPolyData(poly, 'Scalars_', (i+1, i+1),'cell')
        if poly_i.GetNumberOfPoints() == 0:
            print("Mesh based methods.")
            poly_i = thresholdPolyData(poly, 'RegionId', (i, i), 'point')
        gt_i = thresholdPolyData(gt, 'Scalars_', (i+1, i+1),'cell')
        pred2gt_dist, pred2gt = surface_distance(gt_i, poly_i)
        gt2pred_dist, gt2pred = surface_distance(poly_i, gt_i)
        assd = (np.mean(pred2gt_dist)+np.mean(gt2pred_dist))/2
        haus = max(np.max(pred2gt_dist), np.max(gt2pred_dist))
        assd_list.append(assd)
        haus_list.append(haus)
        poly_list.append(pred2gt)

    poly_dist = appendPolyData(poly_list)
    # whole heart
    pred2gt_dist, pred2gt = surface_distance(gt, poly)
    gt2pred_dist, gt2pred = surface_distance(poly, gt)

    assd = (np.mean(pred2gt_dist)+np.mean(gt2pred_dist))/2
    haus = max(np.max(pred2gt_dist), np.max(gt2pred_dist))

    assd_list.append(assd)
    haus_list.append(haus)
    print(assd_list)
    print(haus_list)
    return assd_list, haus_list, poly_dist

def evaluate(pred_dir, pred_pat, gt_dir, gt_pat, out_name, num_region=7):
    pred_fns = natural_sort(glob.glob(os.path.join(pred_dir, pred_pat)))
    gt_fns = natural_sort(glob.glob(os.path.join(gt_dir, gt_pat)))

    assd_list, haus_list = [], []
    for pred_fn, gt_fn in zip(pred_fns, gt_fns):
        pred_poly = load_vtk_mesh(pred_fn)
        gt_poly = load_vtk_mesh(gt_fn)
        assd, haus, poly_dist = evaluate_poly(pred_poly, gt_poly, num_region)
        assd_list.append(assd)
        haus_list.append(haus)
        write_vtk_polydata(poly_dist, os.path.join(pred_dir, 'dist_'+out_name+os.path.basename(pred_fn)))

    assd_path = os.path.join(pred_dir, out_name+'assd.csv')
    haus_path = os.path.join(pred_dir, out_name+'haus.csv')

    write_scores(assd_path, assd_list)
    write_scores(haus_path, haus_list)

if __name__ == '__main__':
    num_region = 7
    gt_dir = 'examples/gt'

    pred_dir = 'examples/pred'
    out_name = 'mr_'
    pred_pat = 'block2_mr*.vtp'
    gt_pat = 'mr_*.vtp'
    evaluate(pred_dir, pred_pat, gt_dir, gt_pat, out_name, num_region)
