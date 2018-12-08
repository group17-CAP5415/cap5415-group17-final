from data_generator.object_detection_2d_data_generator import DataGenerator

input_format = ["image_name", "class_id", "xmin", "xmax", "ymin", "ymax"] # order of columns in csv

def convert_to_h5(images_dir, annotation_csv, h5_file_name):
    dataset = DataGenerator(load_images_into_memory=False)

    dataset.parse_csv(
        images_dir,
        annotation_csv,
        input_format,
        verbose=True
    )

    dataset.create_hdf5_dataset(
        file_path=h5_file_name + ".h5",
        verbose=True)
    return

convert_to_h5("./FLIR_ADAS/training/PreviewData", "./training.csv", "training")
convert_to_h5("./FLIR_ADAS/validation/PreviewData", "./validation.csv", "validation")
convert_to_h5("./FLIR_ADAS/video/PreviewData", "./video.csv", "video")