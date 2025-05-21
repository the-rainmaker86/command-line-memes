#!/usr/bin/env bash
# This script generates a meme using the provided image and text.
# It requires the 'convert' command from ImageMagick to be installed.
# Usage: ./meme.sh <image_path> <top_text> <bottom_text>
# Example: ./meme.sh image.jpg "Top Text" "Bottom Text"
# Check if the required commands are available
if ! command -v convert &> /dev/null
then
    echo "Error: ImageMagick is not installed. Please install it to use this script."
    exit 1
fi 

# Function to calculate font size based on image dimensions
calculate_font_size() {
    local width=$1
    local base_size=70
    local min_size=40
    local max_size=150
    local reference_width=800
    
    # Calculate scale factor
    local scale_factor=$(echo "scale=2; $width / $reference_width" | bc)
    
    # Calculate new font size
    local new_size=$(echo "scale=0; $base_size * $scale_factor / 1" | bc)
    
    # Clamp between min and max sizes
    if [ $new_size -lt $min_size ]; then
        new_size=$min_size
    elif [ $new_size -gt $max_size ]; then
        new_size=$max_size
    fi
    
    echo $new_size
}

# Get the image path, top text, and bottom text from the command line arguments
image_path=$1
top_text=$2
bottom_text=$3

# Get image dimensions
width=$(identify -format "%w" "$image_path")
height=$(identify -format "%h" "$image_path")

# Calculate dynamic font size
font_size=$(calculate_font_size $width)

# Check if the input file is a GIF
echo "Input file: $image_path"
file "$image_path"

if file "$image_path" | grep -q "GIF image data"; then    
    mkdir -p gif_frames
    convert "$image_path" gif_frames/frame_%04d.png
    echo "it's a gif"

    # Get original delay (fps) from the GIF
    delay=$(identify -format "%T\n" "$image_path" | head -n 1)
    if [ -z "$delay" ]; then
        delay=10  # Default delay if not found
    fi

    # Caption each frame
    for frame in gif_frames/frame_*.png; do
        convert -background white \
            -font Helvetica \
            -pointsize $font_size \
            -fill black \
            -gravity North \
            -size ${width}x \
            caption:"$top_text" \
            -splice 0x50 \
            "$frame" \
            -gravity South \
            -background white \
            -font Helvetica \
            -pointsize $font_size \
            -fill black \
            -gravity South \
            -size ${width}x \
            caption:"$bottom_text" \
            -splice 0x50 \
            -append \
            -fuzz 10% \
            -trim \
            -bordercolor white \
            -border 75x50 \
            "$frame"
    done

    # Reassemble the frames into a new GIF with original delay
    convert -delay $delay -loop 0 gif_frames/frame_*.png captioned_"$image_path"

    # Clean up temporary frames
    rm -r gif_frames
else
    # Process static images
    convert -background white \
        -font Helvetica \
        -pointsize $font_size \
        -fill black \
        -gravity North \
        -size ${width}x \
        caption:"$top_text" \
        -splice 0x50 \
        "$image_path" \
        -gravity South \
        -background white \
        -font Helvetica \
        -pointsize $font_size \
        -fill black \
        -gravity South \
        -size ${width}x \
        caption:"$bottom_text" \
        -splice 0x50 \
        -append \
        -fuzz 10% \
        -trim \
        -bordercolor white \
        -border 75x50 \
        meme.png
fi

