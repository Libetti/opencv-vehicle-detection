from pixellib.instance import instance_segmentation

segment_video = instance_segmentation()
segment_video.load_model("C:/Program Files (x86)/Projects/CADSR/VehicleDetection/trainedModels/mask_rcnn_coco.h5")
segment_video.process_video("C:/Program Files (x86)/Projects/CADSR/VehicleDetection/RawTrafficFootage/british_highway_traffic.mp4", show_bboxes = True, frames_per_second = 25, output_video_name="traffic_monitor.mp4")