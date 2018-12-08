import json
import os
import glob
import pandas
import itertools
from multiprocessing import Pool

def parse_file(json_filename, image_dir_path):
    col_order = ["image_name", "class_id", "xmin", "xmax", "ymin", "ymax"]
    fd = open(json_filename, 'r')
    file_dict = json.load(fd)
    fd.close()

    #image_name = file_dict['image']['file_name'] + ".jpeg" #FUCK
    (_, image_name_withext) = os.path.split(json_filename)
    (image_name, _) = os.path.splitext(image_name_withext)
    image_name = image_name + ".jpeg"
    fname = os.path.join(image_dir_path, image_name)
    if not os.path.isfile(fname):
        print("{} does not exist.".format(fname))
        print(json_filename)
    ground_truths = file_dict['annotation']
    
    def gt_to_df_row(gt):
        class_id = int(gt['category_id'])
        bbox = gt['bbox']

        [x, y, w, h] = map(float, bbox)
        xmin = int(x); xmax = int(x + w);
        ymin = int(y); ymax = int(y + h);

        data_row = {"image_name":image_name, "class_id":class_id, "xmin":xmin, "xmax":xmax, "ymin":ymin, "ymax":ymax}
        df_row = pandas.DataFrame(data=data_row, columns= col_order, index=[0])
        return df_row
    
    rows = list(map(gt_to_df_row, ground_truths))
    if rows:
        image_df = pandas.concat(rows, ignore_index=True)
    else:
        #print("{} has no bounding boxes.".format(image_name))
        image_df = pandas.DataFrame(columns=col_order)
    return image_df

def json_annotations_to_csv(annotation_dir_path, image_dir_path, csv_basename):
    print(annotation_dir_path, os.path.isdir(annotation_dir_path))
    print(image_dir_path, os.path.isdir(image_dir_path))

    glob_pattern = os.path.join(annotation_dir_path, "*.json")
    json_files = glob.glob(glob_pattern)
    print("Found {} json files.".format(len(json_files)))

    cpus = os.cpu_count()
    print("{} CPUs.".format(cpus))
    nworkers = cpus * 1
    with Pool(processes=nworkers) as pool:
        image_dataframes = pool.starmap(parse_file, zip(json_files, itertools.repeat(image_dir_path)))
    whole_dataframe = pandas.concat(image_dataframes, ignore_index=True)

    #print(whole_dataframe)
    #print("Original class_ids:")
    #print(whole_dataframe.groupby('class_id')['class_id'].count())

    class_mappings = {
        18 : 17, # Dog -> 17 (dog)
        91 : 8, # Other vehicle -> 8 (truck)
    }
    whole_dataframe = whole_dataframe.replace({"class_id":class_mappings})
    print("Re-mapped class_ids:")
    print(whole_dataframe.groupby('class_id')['class_id'].count())

    whole_dataframe.to_csv(path_or_buf=csv_basename+".csv", index=False)
    print("Done. Wrote {} bounding boxes to {}.csv.".format(whole_dataframe.shape[0], csv_basename))

if __name__ == '__main__':
    print(os.getcwd())
    json_annotations_to_csv("./FLIR_ADAS/training/Annotations", "./FLIR_ADAS/training/PreviewData", "training")
    json_annotations_to_csv("./FLIR_ADAS/validation/Annotations", "./FLIR_ADAS/validation/PreviewData", "validation")
    json_annotations_to_csv("./FLIR_ADAS/video/Annotations", "./FLIR_ADAS/video/PreviewData", "video")