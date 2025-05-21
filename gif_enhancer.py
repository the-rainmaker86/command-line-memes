from PIL import Image, ImageDraw, ImageFont
import imageio
import numpy as np
import os
import sys

def enhance_gif(input_path, output_path, scale_factor=2, fps=15, quality=90):
    """
    Enhance a GIF by increasing resolution, optimizing frame rate, and improving quality.
    
    Args:
        input_path: Path to input GIF
        output_path: Path to save enhanced GIF
        scale_factor: How much to increase the size (default: 2x)
        fps: Frames per second (default: 15)
        quality: Output quality (0-100, default: 90)
    """
    # Read the GIF
    gif = imageio.get_reader(input_path)
    
    # Get the first frame to determine dimensions
    first_frame = gif.get_data(0)
    new_width = first_frame.shape[1] * scale_factor
    new_height = first_frame.shape[0] * scale_factor
    
    # Create a writer for the enhanced GIF
    writer = imageio.get_writer(output_path, fps=fps, quality=quality, loop=0)
    
    # Process each frame
    for frame in gif:
        # Convert to PIL Image
        pil_frame = Image.fromarray(frame)
        
        # Resize with high-quality resampling
        pil_frame = pil_frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert back to numpy array
        enhanced_frame = np.array(pil_frame)
        
        # Write the enhanced frame
        writer.append_data(enhanced_frame)
    
    writer.close()

def wrap_text(text, font, max_width):
    """
    Wrap text to fit within max_width.
    Returns a list of wrapped lines.
    """
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        # Create a test line with the current word
        test_line = ' '.join(current_line + [word])
        # Get the width of the test line
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def add_caption_to_gif(input_path, output_path, top_caption=None, bottom_caption=None, 
                      font_size=30, font_color=(255, 255, 255), stroke_color=(0, 0, 0),
                      margin=20, border_size=50, min_border_size=100):
    """
    Add captions to a GIF with improved text rendering and white border.
    
    Args:
        input_path: Path to input GIF
        output_path: Path to save captioned GIF
        top_caption: Text to add at the top (optional)
        bottom_caption: Text to add at the bottom (optional)
        font_size: Size of the font
        font_color: RGB color of the text
        stroke_color: RGB color of the text outline
        margin: Distance from the edge in pixels
        border_size: Size of the white border in pixels
        min_border_size: Minimum size of the border when text is present
    """
    # Read the GIF
    gif = imageio.get_reader(input_path)
    
    # Get the first frame to determine dimensions
    first_frame = gif.get_data(0)
    width, height = first_frame.shape[1], first_frame.shape[0]
    
    # Load a font (you may need to specify a different font path)
    try:
        font = ImageFont.truetype("Verdana", font_size)
    except:
        font = ImageFont.load_default()
    
    # Process top caption if provided
    top_lines = []
    top_height = 0
    if top_caption:
        max_width = width + (2 * border_size) - (2 * margin)
        top_lines = wrap_text(top_caption, font, max_width)
        line_height = font_size + 5
        top_height = len(top_lines) * line_height
        required_top_border = top_height + (2 * margin)
    else:
        required_top_border = 0
    
    # Process bottom caption if provided
    bottom_lines = []
    bottom_height = 0
    if bottom_caption:
        max_width = width + (2 * border_size) - (2 * margin)
        bottom_lines = wrap_text(bottom_caption, font, max_width)
        line_height = font_size + 5
        bottom_height = len(bottom_lines) * line_height
        required_bottom_border = bottom_height + (2 * margin)
    else:
        required_bottom_border = 0
    
    # Calculate required border sizes
    required_top = max(required_top_border, min_border_size if top_caption else 0)
    required_bottom = max(required_bottom_border, min_border_size if bottom_caption else 0)
    
    # Calculate new dimensions with borders
    new_width = width + (2 * border_size)  # Keep side borders the same
    new_height = height + (2 * border_size) + required_top + required_bottom
    
    # Get FPS from metadata or use default
    try:
        fps = gif.get_meta_data()['fps']
    except (KeyError, TypeError):
        fps = 15  # Default FPS if not found in metadata
    
    # Create a writer for the captioned GIF
    writer = imageio.get_writer(output_path, fps=fps, loop=0)
    
    # Process each frame
    for frame in gif:
        # Convert to PIL Image
        pil_frame = Image.fromarray(frame)
        
        # Create a new image with white background
        bordered_frame = Image.new('RGB', (new_width, new_height), 'white')
        
        # Paste the original frame in the center
        bordered_frame.paste(pil_frame, (border_size, border_size + required_top))
        
        draw = ImageDraw.Draw(bordered_frame)
        
        # Draw top caption if provided
        if top_caption:
            y = (required_top - top_height) // 2  # Center in top border
            for line in top_lines:
                text_bbox = draw.textbbox((0, 0), line, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                x = (new_width - text_width) // 2
                
                # Draw text with stroke (outline)
                for offset_x, offset_y in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                    draw.text((x + offset_x, y + offset_y), line, font=font, fill=stroke_color)
                
                # Draw main text
                draw.text((x, y), line, font=font, fill=font_color)
                
                # Move to next line
                y += font_size + 5
        
        # Draw bottom caption if provided
        if bottom_caption:
            y = new_height - required_bottom + (required_bottom - bottom_height) // 2
            for line in bottom_lines:
                text_bbox = draw.textbbox((0, 0), line, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                x = (new_width - text_width) // 2
                
                # Draw text with stroke (outline)
                for offset_x, offset_y in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                    draw.text((x + offset_x, y + offset_y), line, font=font, fill=stroke_color)
                
                # Draw main text
                draw.text((x, y), line, font=font, fill=font_color)
                
                # Move to next line
                y += font_size + 5
        
        # Convert back to numpy array
        captioned_frame = np.array(bordered_frame)
        
        # Write the captioned frame
        writer.append_data(captioned_frame)
    
    writer.close()

# Example usage
if __name__ == "__main__":
    input_path = sys.argv[1]  # Full path to input GIF
    input_filename = input_path.split('/')[-1]  # Just the filename
    enhanced_gif = f"enhanced-{input_filename}"  # Temporary enhanced version
    final_gif = f"final-{input_filename}"       # Final output with caption
    
    # Get captions from command line arguments
    top_caption = sys.argv[2] if len(sys.argv) > 2 else None
    bottom_caption = sys.argv[3] if len(sys.argv) > 3 else None
    
    # First enhance the GIF
    enhance_gif(input_path, enhanced_gif, 
               scale_factor=2,    # Increase size (adjust as needed)
               fps=24,            # Frames per second
               quality=90)        # Quality (0-100)
    
    # Then add captions with white border
    add_caption_to_gif(enhanced_gif, final_gif, 
                      top_caption=top_caption,
                      bottom_caption=bottom_caption,
                      font_size=70,          # Adjust text size
                      font_color=(0,0,0),     # Black text
                      stroke_color=(255,255,255), # White outline
                      border_size=50,         # Base border size
                      min_border_size=100)    # Minimum border size when text is present 