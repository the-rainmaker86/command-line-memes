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

def add_caption_to_gif(input_path, output_path, caption, font_size=30, 
                      font_color=(255, 255, 255), stroke_color=(0, 0, 0),
                      position='top', margin=20, border_size=50, min_border_size=100):
    """
    Add a caption to a GIF with improved text rendering and white border.
    
    Args:
        input_path: Path to input GIF
        output_path: Path to save captioned GIF
        caption: Text to add as caption
        font_size: Size of the font
        font_color: RGB color of the text
        stroke_color: RGB color of the text outline
        position: 'top' or 'bottom' to control vertical position
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
    
    # Wrap the caption text
    max_width = width + (2 * border_size) - (2 * margin)  # Leave some margin on the sides
    wrapped_lines = wrap_text(caption, font, max_width)
    
    # Calculate total height of wrapped text
    line_height = font_size + 5  # Add some padding between lines
    total_text_height = len(wrapped_lines) * line_height
    
    # Calculate required border size for text
    required_border = total_text_height + (2 * margin)  # Add margin above and below text
    
    # Use the larger of the required border or minimum border size
    actual_border_size = max(required_border, min_border_size)
    
    # Calculate new dimensions with border
    new_width = width + (2 * border_size)  # Keep side borders the same
    new_height = height + (2 * border_size) + (actual_border_size - border_size)  # Add extra height for text
    
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
        bordered_frame.paste(pil_frame, (border_size, actual_border_size))
        
        draw = ImageDraw.Draw(bordered_frame)
        
        # Calculate starting y position based on desired location
        if position.lower() == 'top':
            y = (actual_border_size - total_text_height) // 2  # Center in top border
        else:  # bottom
            y = new_height - border_size + (border_size - total_text_height) // 2  # Center in bottom border
        
        # Draw each line of wrapped text
        for line in wrapped_lines:
            # Calculate text position for this line
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            x = (new_width - text_width) // 2
            
            # Draw text with stroke (outline)
            for offset_x, offset_y in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                draw.text((x + offset_x, y + offset_y), line, font=font, fill=stroke_color)
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=font_color)
            
            # Move to next line
            y += line_height
        
        # Convert back to numpy array
        captioned_frame = np.array(bordered_frame)
        
        # Write the captioned frame
        writer.append_data(captioned_frame)
    
    writer.close()

# Example usage
if __name__ == "__main__":
    input_gif = sys.argv[1]  # Your input GIF
    enhanced_gif = f"enhanced-{input_gif}"  # Temporary enhanced version
    final_gif = f"final-{input_gif}"       # Final output with caption
    
    # First enhance the GIF
    enhance_gif(input_gif, enhanced_gif, 
               scale_factor=2,    # Increase size (adjust as needed)
               fps=15,            # Frames per second
               quality=90)        # Quality (0-100)
    
    # Then add caption at the top with white border
    add_caption_to_gif(enhanced_gif, final_gif, 
                      sys.argv[2],
                      font_size=70,          # Adjust text size
                      font_color=(0,0,0),     # Black text
                      stroke_color=(255,255,255), # White outline
                      position='top',         # Place caption at top
                      border_size=50,         # Base border size
                      min_border_size=100)    # Minimum border size when text is present 