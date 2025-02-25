import streamlit as st
import numpy as np
from PIL import Image
import io
import tempfile
import os

def main():
    st.title("Digital Image Processing System")
    
    # User information
    st.header("User Information")
    name = st.text_input("Enter your name")
    reg_no = st.text_input("Enter your registration number (Format: 2000-AG-1000)")
    
    # Validate registration number format
    is_valid_reg = False
    if reg_no:
        import re
        pattern = r'^\d{4}-[aA][gG]-\d{4}$'
        is_valid_reg = bool(re.match(pattern, reg_no))
        if not is_valid_reg:
            st.error("Please enter a valid registration number in the format 2000-AG-1000")
    
    # Image upload
    st.header("Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None and name and is_valid_reg:
        # Read image
        image = Image.open(uploaded_file).convert('RGB')
        img_array = np.array(image)
        
        st.header("Original Image")
        st.image(image, caption="Original Image", use_column_width=True)
        
        # Image Operations - with checkboxes
        st.header("Image Operations")
        
        # Create a select all checkbox
        select_all = st.checkbox("Select All Operations")
        
        # If select all is checked, check all other boxes
        addition = st.checkbox("Addition", value=select_all)
        subtraction = st.checkbox("Subtraction", value=select_all)
        multiplication = st.checkbox("Multiplication", value=select_all)
        division = st.checkbox("Division", value=select_all)
        
        # Value for operation
        value = st.slider("Select value for operation", 0, 255, 50)
        
        # Process button
        if st.button("Process Image"):
            # Check if at least one operation is selected
            if not (addition or subtraction or multiplication or division):
                st.error("Please select at least one operation")
            else:
                # Store processed images in a dictionary
                processed_images = {}
                
                if addition:
                    processed_images["Addition"] = apply_operation(img_array, "Addition", value)
                
                if subtraction:
                    processed_images["Subtraction"] = apply_operation(img_array, "Subtraction", value)
                
                if multiplication:
                    processed_images["Multiplication"] = apply_operation(img_array, "Multiplication", value)
                
                if division:
                    processed_images["Division"] = apply_operation(img_array, "Division", value)
                
                # Create simple PDF directly to a file
                try:
                    # Display success message
                    with st.spinner("Generating PDF..."):
                        pdf_path = create_simple_pdf(name, reg_no, img_array, processed_images)
                        
                        # Read the PDF file into memory
                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()
                        
                        # Remove the temporary file
                        os.remove(pdf_path)
                        
                    st.success("Processing complete! Download your PDF to view results.")
                    
                    # Download button with proper byte format
                    st.download_button(
                        label="Download as PDF",
                        data=pdf_bytes,
                        file_name=f"{reg_no}_image_processing.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")

def apply_operation(img_array, operation, value):
    # Convert to float32 for operations
    img_float = img_array.astype(np.float32)
    
    if operation == "Addition":
        result = np.clip(img_float + value, 0, 255)
    elif operation == "Subtraction":
        result = np.clip(img_float - value, 0, 255)
    elif operation == "Multiplication":
        result = np.clip(img_float * (value/50), 0, 255)  # Scaling factor
    elif operation == "Division":
        # Avoid division by zero
        if value == 0:
            value = 1
        result = np.clip(img_float / (value/50), 0, 255)  # Scaling factor
    
    return result.astype(np.uint8)

def create_simple_pdf(name, reg_no, original_img, processed_images):
    # Use a different approach: write directly to a file
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    pdf_path = temp_file.name
    
    # Save images to temporary files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save original image
        orig_path = os.path.join(temp_dir, "original.jpg")
        Image.fromarray(original_img).save(orig_path, format="JPEG")
        
        # Save processed images
        processed_paths = {}
        for op_name, img_array in processed_images.items():
            img_path = os.path.join(temp_dir, f"{op_name.lower()}.jpg")
            Image.fromarray(img_array).save(img_path, format="JPEG")
            processed_paths[op_name] = img_path
        
        # Create PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Digital Image Processing Report")
        
        # User Info
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Name: {name}")
        c.drawString(50, height - 100, f"Registration Number: {reg_no}")
        
        # Draw original image
        c.drawString(50, height - 130, "Original Image:")
        c.drawImage(orig_path, 50, height - 330, width=width-100, height=200, preserveAspectRatio=True)
        
        # Keep track of vertical position
        y_position = height - 350
        
        # Add operations results
        for operation, img_path in processed_paths.items():
            # Add a new page for each operation
            c.showPage()
            
            # Reset font and title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Digital Image Processing Report")
            
            # Add operation name
            c.setFont("Helvetica", 14)
            c.drawString(50, height - 80, f"{operation} Result:")
            
            # Add processed image
            c.drawImage(img_path, 50, height - 280, width=width-100, height=200, preserveAspectRatio=True)
        
        c.save()
    
    return pdf_path

if __name__ == "__main__":
    main()