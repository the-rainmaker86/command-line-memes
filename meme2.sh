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


# Get the image path, top text, and bottom text from the command line arguments
image_path=$1
top_text=$2
bottom_text=$3

# Generate the meme using ImageMagick with word wrapping

# convert -background white -font Helvetica -pointsize 100 -gravity North -size 1600x caption:"$top_text" \
#     $image_path -gravity South -background white -font Helvetica -pointsize 100 -gravity South -size 1600x caption:"$bottom_text" \
#     -append meme.jpg
# convert -background white -font Helvetica -pointsize 100 -fill black -gravity North -size 1600x caption:"$top_text" \
#     -splice 0x50 $image_path -gravity South -background white -font Helvetica -pointsize 100 -fill black -gravity South -size 1600x caption:"$bottom_text" \
#     -splice 0x50 -append -fuzz 10% -trim -bordercolor white -border 75x50 meme.png
        
# if [ $? -eq 0 ]; then
#     echo "Meme opened successfully."
# else
#     echo "Error: Failed to open meme."
#     exit 1
# fi
# This script is for educational purposes only
# It is not recommended to run infinite loops in production environments

# Check if the input file is a GIF
echo "Input file: $image_path"
file "$image_path"

if file "$image_path" | grep -q "GIF image data"; then    
    mkdir -p gif_frames
    convert "$image_path" gif_frames/frame_%04d.png
    echo "it's a gif"

    # Caption each frame
    for frame in gif_frames/frame_*.png; do
        convert -background white -font Helvetica -pointsize 100 -fill black -gravity North -size 1600x caption:"$top_text" \
            -splice 0x50 "$frame" -gravity South -background white -font Helvetica -pointsize 100 -fill black -gravity South -size 1600x caption:"$bottom_text" \
            -splice 0x50 -append -fuzz 10% -trim -bordercolor white -border 75x50 "$frame"
    done

    # Reassemble the frames into a new GIF
    convert -delay 0 -loop 0 gif_frames/frame_*.png captioned_"$image_path"

    # Clean up temporary frames
    # rm -r gif_frames
else
    # Process static images
    convert -background white -font Helvetica -pointsize 100 -fill black -gravity North -size 1600x caption:"$top_text" \
        -splice 0x50 "$image_path" -gravity South -background white -font Helvetica -pointsize 100 -fill black -gravity South -size 1600x caption:"$bottom_text" \
        -splice 0x50 -append -fuzz 10% -trim -bordercolor white -border 75x50 meme.png
fi

