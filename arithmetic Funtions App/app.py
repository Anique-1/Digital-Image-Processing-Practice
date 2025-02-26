import streamlit as st
import numpy as np
from PIL import Image
import io
import tempfile
import os

def main():
    st.title("Digital Image Processing System")
    
    # User Information
    st.header("User Information")
    name = st.text_input("Enter your name")
    reg_no = st.text_input("Enter your registration number (Format: 2000-AG-1000)")
    
    # Validate registration number
    is_valid_reg = False
    if reg_no:
        import re
        pattern = r'^\d{4}-[aA][gG]-\d{4}$'
        is_valid_reg = bool(re.match(pattern, reg_no))
        if not is_valid_reg:
            st.error("Please enter a valid registration number in the format 2000-AG-1000")
    
    # Upload Images
    st.header("Upload Images")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file1 = st.file_uploader("Choose first image...", type=["jpg", "jpeg", "png"])
        
    with col2:
        uploaded_file2 = st.file_uploader("Choose second image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file1 is not None and uploaded_file2 is not None and name and is_valid_reg:
        # Load and display original images
        image1 = Image.open(uploaded_file1).convert('RGB')
        image2 = Image.open(uploaded_file2).convert('RGB')
        
        # Resize second image to match first image dimensions
        image2 = image2.resize(image1.size)
        
        img_array1 = np.array(image1)
        img_array2 = np.array(image2)
        
        st.header("Original Images")
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(image1, caption="Image One", use_column_width=True)
        with col2:
            st.image(image2, caption="Image Two", use_column_width=True)
        
        # Image Operations
        st.header("Image Operations")
        
        # Select operations
        select_all = st.checkbox("Select All Operations")
        
        addition = st.checkbox("Addition", value=select_all)
        subtraction = st.checkbox("Subtraction", value=select_all)
        multiplication = st.checkbox("Multiplication", value=select_all)
        division = st.checkbox("Division", value=select_all)
        
        # Weight factor for blending
        weight = st.slider("Weight factor for Image One (0 to 1)", 0.0, 1.0, 0.5, step=0.1)
        
        # Process button
        if st.button("Process Images"):
            
            if not (addition or subtraction or multiplication or division):
                st.error("Please select at least one operation")
            else:
                # Create dictionary to store processed images
                processed_images = {}
                
                if addition:
                    processed_images["Addition"] = apply_operation_two_images(img_array1, img_array2, "Addition", weight)
                
                if subtraction:
                    processed_images["Subtraction"] = apply_operation_two_images(img_array1, img_array2, "Subtraction", weight)
                
                if multiplication:
                    processed_images["Multiplication"] = apply_operation_two_images(img_array1, img_array2, "Multiplication", weight)
                
                if division:
                    processed_images["Division"] = apply_operation_two_images(img_array1, img_array2, "Division", weight)
                
                # Display results
                for operation, result_img in processed_images.items():
                    st.subheader(f"{operation} Result")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.image(image1, caption="Image One", use_column_width=True)
                    with col2:
                        st.image(image2, caption="Image Two", use_column_width=True)
                    with col3:
                        st.image(result_img, caption="Result", use_column_width=True)
                
                # Generate PDF
                try:
                    with st.spinner("Generating PDF..."):
                        pdf_path = create_two_image_pdf(name, reg_no, img_array1, img_array2, processed_images)
                        
                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()
                        
                        os.remove(pdf_path)
                        
                    st.success("Processing complete! Download your PDF to view results.")
                    
                    st.download_button(
                        label="Download as PDF",
                        data=pdf_bytes,
                        file_name=f"{reg_no}_image_processing.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")

def apply_operation_two_images(img_array1, img_array2, operation, weight=0.5):
    """Apply operations between two images with a weight factor for blending"""
    
    img1_float = img_array1.astype(np.float32)
    img2_float = img_array2.astype(np.float32)
    
    if operation == "Addition":
        # Weighted addition
        result = np.clip(weight * img1_float + (1 - weight) * img2_float, 0, 255)
    elif operation == "Subtraction":
        # Weighted subtraction
        result = np.clip(weight * img1_float - (1 - weight) * img2_float, 0, 255)
    elif operation == "Multiplication":
        # Element-wise multiplication (normalized)
        result = np.clip((img1_float * img2_float) / 255.0, 0, 255)
    elif operation == "Division":
        # Avoid division by zero by adding a small epsilon
        epsilon = 1e-10
        result = np.clip(img1_float / (img2_float + epsilon) * 127.5, 0, 255)
    
    return result.astype(np.uint8)

def create_two_image_pdf(name, reg_no, img_array1, img_array2, processed_images):
    """Create a PDF with two input images and the resulting processed images"""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    # Create a temporary file to store the PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    pdf_path = temp_file.name
    
    # Use a temporary directory to store the images
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # Save original images
        img1_path = os.path.join(temp_dir, "image1.jpg")
        img2_path = os.path.join(temp_dir, "image2.jpg")
        Image.fromarray(img_array1).save(img1_path, format="JPEG")
        Image.fromarray(img_array2).save(img2_path, format="JPEG")
        
        # Save processed images
        processed_paths = {}
        for op_name, img_array in processed_images.items():
            img_path = os.path.join(temp_dir, f"{op_name.lower()}.jpg")
            Image.fromarray(img_array).save(img_path, format="JPEG")
            processed_paths[op_name] = img_path
        
        # Create the PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # Title page
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Digital Image Processing Report")
        
        # User information
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Name: {name}")
        c.drawString(50, height - 100, f"Registration Number: {reg_no}")
        
        # Original images
        c.drawString(50, height - 130, "Original Images:")
        
        # Draw first image
        c.drawImage(img1_path, 50, height - 330, width=(width-100)/2, height=180, preserveAspectRatio=True)
        c.drawString(50, height - 350, "Image One")
        
        # Draw second image
        c.drawImage(img2_path, width/2, height - 330, width=(width-100)/2, height=180, preserveAspectRatio=True)
        c.drawString(width/2, height - 350, "Image Two")
        
        # Create a page for each operation
        for operation, img_path in processed_paths.items():
            c.showPage()
            
            # Page header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Digital Image Processing Report")
            
            # Operation name
            c.setFont("Helvetica", 14)
            c.drawString(50, height - 80, f"{operation} Operation:")
            
            # Draw first image
            img_width = (width-120)/3
            img_height = 180
            
            c.drawImage(img1_path, 50, height - 280, width=img_width, height=img_height, preserveAspectRatio=True)
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 300, "Image One")
            
            # Draw second image
            c.drawImage(img2_path, 60 + img_width, height - 280, width=img_width, height=img_height, preserveAspectRatio=True)
            c.drawString(60 + img_width, height - 300, "Image Two")
            
            # Draw result image
            c.drawImage(img_path, 70 + img_width*2, height - 280, width=img_width, height=img_height, preserveAspectRatio=True)
            c.drawString(70 + img_width*2, height - 300, "Result")
        
        c.save()
    
    return pdf_path

if __name__ == "__main__":
    main()