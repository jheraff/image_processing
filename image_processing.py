import argparse
import os
import subprocess
import json
import re
import tempfile
import sys

parser = argparse.ArgumentParser(description="Process images using ffmpeg")
parser.add_argument("input", help="Input image files")
parser.add_argument("-w", "--watermark", action="store_true", help="Add watermark")
parser.add_argument("-g", "--gif", action="store_true", help="Create GIF")
parser.add_argument("-t", "--thumbnail", action="store_true", help="Create thumbnail")
parser.add_argument("-m", "--metadata", action="store_true", help="Export metadata")
args = parser.parse_args()

# python project3.py Proj3_VFX/Bath_VFX_v01.JPG -w
# python project3.py Proj3_VFX/Pirate_VFX_v02.JPG -w -t
# python project3.py Proj3_VFX/ -w -g -m

input_path = os.path.abspath(args.input)

if os.path.isdir(input_path):
    output_dir = input_path
else:
    output_dir = os.path.dirname(input_path) or "." 

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def find_image_files(path):
    image_extensions = ['.png', '.jpg', '.jpeg']
    files = []
    
    if os.path.isdir(path):
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if (os.path.isfile(file_path) and 
                os.path.splitext(file)[1].lower() in image_extensions):
                files.append(file_path)
    elif os.path.isfile(path):
        if os.path.splitext(path)[1].lower() in image_extensions:
            files.append(path)
    
    return sorted(files)

image_files = find_image_files(input_path)

if not image_files:
    print("No image files found")
    sys.exit(1)

def get_clean_base_name(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    return re.sub(r'_v\d+$', '', base)

if os.path.isdir(input_path):
    folder_base_name = os.path.basename(input_path)
else:
    folder_base_name = get_clean_base_name(input_path)

all_output_files = []

def run_ffmpeg(args, description):
    try:
        subprocess.run(
            ['ffmpeg'] + args, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        return False

def get_next_version(directory, prefix, base_name):
    max_version = 0
    pattern = f"{prefix}_{base_name}_v(\\d+)"
    
    for file in os.listdir(directory):
        file_base = os.path.splitext(file)[0]
        match = re.match(pattern, file_base)
        if match:
            max_version = max(max_version, int(match.group(1)))
    
    return max_version + 1

for image_file in image_files:
    print(f"Processing: {os.path.basename(image_file)}")
    
    exact_filename = os.path.basename(image_file)
    base_name = get_clean_base_name(image_file)
    
    if args.watermark and args.thumbnail:
        version = get_next_version(output_dir, "WMTC", base_name)
        output_path = os.path.join(output_dir, f"WMTC_{base_name}_v{version:02d}.jpg")
        
        success = run_ffmpeg([
            '-i', image_file,
            '-vf', f"scale=1280:720:force_original_aspect_ratio=decrease,"
                   f"pad=1280:720:(ow-iw)/2:(oh-ih)/2,"
                   f"drawtext=text='{folder_base_name}':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=40",
            '-y', output_path
        ], "creating watermarked thumbnail")
        
        if success:
            all_output_files.append(output_path)
    else:
        if args.watermark:
            version = get_next_version(output_dir, "WM", base_name)
            output_path = os.path.join(output_dir, f"WM_{base_name}_v{version:02d}.jpg")
            
            success = run_ffmpeg([
                '-i', image_file,
                '-vf', f"drawtext=text='{folder_base_name}':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=400",
                '-y', output_path
            ], "creating watermarked image")
            
            if success:
                all_output_files.append(output_path)
        
        if args.thumbnail:
            version = get_next_version(output_dir, "TC", base_name)
            output_path = os.path.join(output_dir, f"TC_{base_name}_v{version:02d}.jpg")
            
            success = run_ffmpeg([
                '-i', image_file,
                '-vf', f"scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
                '-y', output_path
            ], "creating thumbnail")
            
            if success:
                all_output_files.append(output_path)

if args.gif and image_files:
    prefix = "WMGC" if args.watermark else "GC"
    gif_output_path = os.path.join(output_dir, f"{prefix}_VFX_01.gif")
    
    image_files_for_gif = image_files
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        for img in image_files_for_gif:
            absolute_path = os.path.abspath(img)
            temp_file.write(f"file '{absolute_path}'\nduration 2\n")
        
        if image_files_for_gif:
            absolute_path = os.path.abspath(image_files_for_gif[-1])
            temp_file.write(f"file '{absolute_path}'\n")
        
        temp_file_path = temp_file.name
    
    vf_filters = []
    
    vf_filters.append("scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2")
    
    if args.watermark:
        vf_filters.append(f"drawtext=text='{folder_base_name}':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=30")
    
    vf_filters.append("split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse")
    
    vf_param = ",".join(vf_filters)
    
    success = run_ffmpeg([
        '-f', 'concat',
        '-safe', '0',
        '-i', temp_file_path,
        '-vf', vf_param,
        '-loop', '0', 
        '-y', gif_output_path
    ], "creating GIF")
    
    os.unlink(temp_file_path)
        
    if success:
        watermark_status = "watermarked " if args.watermark else ""
        all_output_files.append(gif_output_path)

if args.metadata:
    meta_output_path = os.path.join(output_dir, "ME_VFX_01.txt")
    
    with open(meta_output_path, 'w') as f:
        f.write(f"Number images processed: {len(image_files)}\n")
        
        for idx, image_file in enumerate(image_files, 1):
            f.write(f"\n{idx}. {image_file}\n{'-'*50}\n")
            
            result = subprocess.run([
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                image_file
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)
                
                if 'format' in metadata and 'size' in metadata['format']:
                    size_bytes = int(metadata['format']['size'])
                    size_kb = size_bytes / 1024
                    f.write(f"File size: {size_kb:.2f} KB\n")
                
                for stream in metadata.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        f.write(f"Image format: {stream.get('codec_name', 'Unknown')}\n")
                        f.write(f"Dimensions: {stream.get('width', '?')}x{stream.get('height', '?')}\n")
                        if 'bits_per_raw_sample' in stream:
                            f.write(f"Bit depth: {stream.get('bits_per_raw_sample')} bits\n")
                        break
                
                if 'format' in metadata and 'tags' in metadata['format']:
                    f.write("\nTags:\n")
                    for tag, value in metadata['format']['tags'].items():
                        f.write(f"  {tag}: {value}\n")
            else:
                file_size = os.path.getsize(image_file)
                f.write(f"File size: {file_size / 1024:.2f} KB\n")
        
        if all_output_files:
            f.write("\nOutput:\n")
            for idx, file in enumerate(all_output_files, 1):
                f.write(f"\n{idx}. {file}\n")
                
                file_stat = os.stat(file)
                file_size_kb = file_stat.st_size / 1024
                f.write(f"Size: {file_size_kb:.2f} KB\n")
                
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    img_probe = subprocess.run([
                        'ffprobe', '-v', 'quiet',
                        '-print_format', 'json',
                        '-show_format', '-show_streams',
                        file
                    ], capture_output=True, text=True)
                    
                    if img_probe.returncode == 0 and img_probe.stdout:
                        output_metadata = json.loads(img_probe.stdout)
                        f.write("Full Metadata:\n")
                        
                        if 'format' in output_metadata:
                            for key, value in output_metadata['format'].items():
                                if key != 'tags':  
                                    f.write(f"{key}: {value}\n")
    
    print(f"Exported metadata: {meta_output_path}")
print("Done")
